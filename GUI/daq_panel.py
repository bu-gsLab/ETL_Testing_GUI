import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QVBoxLayout, QFrame, QLabel, QLineEdit, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from pathlib import Path
import multiprocessing
import ipaddress
from queue import Empty

from .panel import Panel
from .rb_panel import RBPanel
from .config import load_hardware_config

from qaqc.session import Session


def run_tests_worker(session_config, slot_tests, status_queue):
    """Run DAQ tests in a spawned process without passing any Qt objects."""
    had_failures = False
    try:
        status_queue.put("Preparing test session...")
        session = Session(**session_config)

        for slot, test_sequence, test_names in slot_tests:
            readable_test_names = [
                test_names.get(test, test.__name__)
                for test in test_sequence
            ]
            print(f"Slot {slot + 1} Tests: {readable_test_names}")
            print("Starting test sequence...")
            session.status_callback = lambda message, slot=slot: status_queue.put(
                f"Slot {slot + 1}: {message}"
            )
            for test_model in test_sequence:
                test_str = test_names.get(test_model, test_model.__name__)
                status_queue.put(f"Slot {slot + 1}: Running {test_str}...")
                for test, result in session.iter_test_sequence(
                    [test_model],
                    slot=slot,
                ):
                    if isinstance(result, Exception):
                        had_failures = True
                        print(f"{test_str} test failed: {result}")
                        status_queue.put(
                            f"Slot {slot + 1}: {test_str} failed — {result}"
                        )
                    else:
                        print(f"{test_str} test passed")
                        status_queue.put(
                            f"Slot {slot + 1}: {test_str} passed"
                        )
    except Exception as e:
        had_failures = True
        print(f"Test process crashed: {e}")
        status_queue.put(f"Test process crashed: {e}")
    finally:
        print("Finished tests")
        status_queue.put(
            "Tests finished with failures"
            if had_failures
            else "Tests finished"
        )


class DAQPanel(Panel):
    def __init__(self, title="Data Acquisition and Testing"):
        super().__init__(title)

        self.daq_process = None
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self.check_process)
        self.active_rb_obj = None
        self.status_queue = None
    
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # ----- Build panels -----

        self.kcu_ip_field = QLineEdit()
        self.kcu_ip_field.setText(load_hardware_config().kcu_ip)
        self.kcu_ip_field.setFixedWidth(250)
        self.kcu_ip_lbl = QLabel("KCU IP: ")
        self.kcu_row = QHBoxLayout()
        self.kcu_row.addWidget(self.kcu_ip_lbl)
        self.kcu_row.addWidget(self.kcu_ip_field)
        self.kcu_row.addStretch()


        self.rb_layout = QVBoxLayout()
        self.rb1 = RBPanel(1)
        self.rb2 = RBPanel(2)
        self.rb_layout.addWidget(self.rb1)
        self.rb_layout.addWidget(self.rb2)

        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 1)
        self.loading_bar.setValue(0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setFixedWidth(180)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ffffff;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #2563eb;
            }
        """)
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: white;")
        self.loading_row = QHBoxLayout()
        self.loading_row.addWidget(self.loading_bar)
        self.loading_row.addWidget(self.status_label)
        self.loading_row.addStretch()

        self.rb1.run_tests_signal.connect(self.create_session)
        self.rb2.run_tests_signal.connect(self.create_session)

        self.rb1.kill_tests_signal.connect(self.kill_process)
        self.rb2.kill_tests_signal.connect(self.kill_process)

        mainlayout = QVBoxLayout()
        mainlayout.addLayout(self.kcu_row)
        mainlayout.addLayout(self.rb_layout)
        mainlayout.addLayout(self.loading_row)

        self.session = None

        self.subgrid.addLayout(mainlayout, 1, 0, 5, 5, Qt.AlignTop)

    def validate_inputs(self, rb_obj):
        try:
            ipaddress.ip_address(self.kcu_ip_field.text())
        except ValueError:
            print(f"Invalid KCU IP: {self.kcu_ip_field.text()}")
            return False

        try:
            rb_ser_num = rb_obj.rb_id_field.text()
            int(rb_ser_num) 
        except ValueError:
            print(f"Invalid RB Serial Number: {rb_ser_num}")
            return False
        
        try:
            for i in range(len(rb_obj.modules)):
                if rb_obj.modules[i].enable_check.isChecked():
                    modid = rb_obj.modules[i].module_id_inputbox.text()
                    int(modid)
                    if int(modid) < 0:
                        raise ValueError
        except ValueError:
            print(f"Invalid Module Serial Number: {modid}")
            return False
        
        try:
            bias = rb_obj.bias_input.text()
            int(bias)
            if abs(int(bias)) > 260: # Don't bias over breakdown
                print("Bias voltage set too high")
                raise ValueError
        except ValueError:
            print(f"Invalid Bias Input: {bias}")
            return False
        
        return True

    def check_process(self):
        self.drain_status_queue()
        if self.daq_process is not None and not self.daq_process.is_alive():
            self.daq_process.join()
            self.drain_status_queue()
            self.process_timer.stop()
            self.finish_tests(self.active_rb_obj)

    def drain_status_queue(self):
        if self.status_queue is None:
            return
        while True:
            try:
                self.status_label.setText(self.status_queue.get_nowait())
            except Empty:
                break

    def create_session(self, rb_obj):
        print(f"Creating session with RB{rb_obj.rb_pos}")
        isValid = self.validate_inputs(rb_obj)
        if not isValid:
            print("Input Validation Failed")
            self.status_label.setText("Input validation failed")
            return
        self.active_rb_obj = rb_obj
        kcu_ip = self.kcu_ip_field.text()
        rb = rb_obj.rb_pos
        rb_size = rb_obj.rb_size
        rb_serial_number = rb_obj.rb_id_field.text()
        modules = [None] * rb_size
        sensor_types = [None] * rb_size
        hybrid_nums = [None] * rb_size
        for i in range(rb_size):
            if rb_obj.modules[i].enable_check.isChecked():
                modules[i] = rb_obj.modules[i].module_id_inputbox.text()
                # keep track of sensor type and number of hybrids on module for setting current compliance
                sensor_types[i] = rb_obj.modules[i].sensor.currentText()
                hybrid_nums[i] = abs(int(rb_obj.modules[i].sensor_num.currentText()))
        

        session_config = dict(
            rb=rb,
            rb_size=rb_size,
            rb_serial_number=rb_serial_number,
            modules=modules,
            kcu_ipaddress=kcu_ip,
            bias_voltage=abs(int(rb_obj.bias_input.text())),
            sensor_types=sensor_types,
            hybrid_nums=hybrid_nums
        )

        rb_tests_str = rb_obj.scroll_container.getCheckedItems()
        rb_tests = [rb_obj.rb_str_to_tests[name] for name in rb_tests_str]
        rb_test_names = {
            test: rb_obj.rb_tests_to_str[test]
            for test in rb_tests
        }
        slot_tests = []
        for i, module in enumerate(modules):
            if module is None:
                continue

            mod_tests_str = rb_obj.modules[i].scroll_container.getCheckedItems()
            mod_tests = []
            for name in mod_tests_str:
                mod_tests.extend(rb_obj.modules[i].module_str_to_tests[name])
            mod_tests = list(dict.fromkeys(mod_tests))

            test_sequence = rb_tests + mod_tests
            test_names = dict(rb_test_names)
            test_names.update({
                test: rb_obj.modules[i].module_tests_to_str[test]
                for test in mod_tests
            })
            slot_tests.append(
                (i, test_sequence, test_names)
            )

        self.status_queue = multiprocessing.Queue()
        self.daq_process = multiprocessing.Process(
            target=run_tests_worker,
            args=(session_config, slot_tests, self.status_queue),
        )
        self.daq_process.start()
        self.loading_bar.setRange(0, 0)
        self.status_label.setText("Starting tests...")
        self.process_timer.start(100)
        rb_obj.test_btn.setEnabled(False)
        rb_obj.kill_test_btn.setEnabled(True)
    
    def kill_process(self, rb_obj):
        if self.daq_process is not None and self.daq_process.is_alive():
            print("Killing test process")

            self.daq_process.terminate()
            self.daq_process.join()

            self.process_timer.stop()
            self.status_label.setText("Tests stopped")
            self.finish_tests(rb_obj)

    def shutdown(self):
        """Stop an active DAQ test process and release its queue."""
        if self.daq_process is not None and self.daq_process.is_alive():
            self.daq_process.terminate()
            self.daq_process.join()
        self.process_timer.stop()
        if self.status_queue is not None:
            self.status_queue.close()
            self.status_queue = None
        self.daq_process = None
        self.active_rb_obj = None

    def finish_tests(self, rb_obj):
        self.daq_process = None
        self.active_rb_obj = None
        self.loading_bar.setRange(0, 1)
        self.loading_bar.setValue(0)
        if self.status_queue is not None:
            self.status_queue.close()
            self.status_queue = None

        rb_obj.test_btn.setEnabled(True)
        rb_obj.kill_test_btn.setEnabled(False)
