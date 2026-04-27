import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QVBoxLayout, QFrame, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from pathlib import Path
import threading
import ipaddress

from .panel import Panel
from .rb_panel import RBPanel

from qaqc.session import Session

class DAQPanel(Panel):
    finish_tests_signal = pyqtSignal(object)
    def __init__(self, title="Data Acquisition and Testing"):
        super().__init__(title)
        self.setStyleSheet("""
        #HVPanel QWidget { color: #ffffff; }
        QLabel { color: #ffffff; }

        QLineEdit, QPlainTextEdit {
            color: #ffffff;
            border: 1px solid #ffffff;
            border-radius: 6px;
            padding: 4px 6px;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
        }

        QPushButton {
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 8px 14px;
            font-weight: 600;
        }
        QPushButton:disabled { color: #9aa5b1; }

        QPushButton#greenButton {
            background-color: #16a34a;
            color: #ffffff;
        }
        QPushButton#greenButton:hover { background-color: #22c55e; }
        QPushButton#greenButton:pressed { background-color: #15803d; }
        QPushButton#greenButton:disabled { background-color: #14532d; color: #9aa5b1;}


        QPushButton#redButton {
            background-color: #e53935;
            color: #ffffff;
        }
        QPushButton#redButton:hover { background-color: #ef5350; }
        QPushButton#redButton:pressed { background-color: #c62828; }
        QPushButton#redButton:disabled { background-color: #7f1d1d; color: #9aa5b1;}
                           
        QPushButton#blueButton {
            background-color: #007bff;
            color: #ffffff;
        }
        QPushButton#blueButton:hover { background-color: #339cff; }
        QPushButton#blueButton:pressed { background-color: #0056b3; }
        """)

        self.daq_stop_evt = None
        self.daq_thread = None
    
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # ----- Build panels -----

        self.kcu_ip_field = QLineEdit()
        self.kcu_ip_field.setFixedSize(250,30)
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

        self.rb1.run_tests_signal.connect(self.create_session)
        self.rb2.run_tests_signal.connect(self.create_session)

        self.rb1.kill_tests_signal.connect(self.kill_thread)
        self.rb2.kill_tests_signal.connect(self.kill_thread)

        mainlayout = QVBoxLayout()
        mainlayout.addLayout(self.kcu_row)
        mainlayout.addLayout(self.rb_layout)

        self.finish_tests_signal.connect(self.finish_tests)

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
            for i in range(len(rb_obj.modules)):
                if rb_obj.modules[i].enable_check.isChecked():
                    bias = rb_obj.modules[i].bias_input.text()
                    int(bias)
                    if abs(int(bias)) > 260: # Don't bias over breakdown
                        print("Bias voltage set too high")
                        raise ValueError
        except ValueError:
            print(f"Invalid Bias Input: {bias}")
            return False
        
        return True

    def create_session(self, rb_obj):
        print(f"Creating session with RB{rb_obj.rb_pos}")
        isValid = self.validate_inputs(rb_obj)
        if not isValid:
            print("Input Validation Failed")
            return
        kcu_ip = self.kcu_ip_field.text()
        rb = rb_obj.rb_pos
        rb_size = rb_obj.rb_size
        rb_serial_number = rb_obj.rb_id_field.text()
        modules = [None] * rb_size
        bias_volts = [None] * rb_size
        sensor_types = [None] * rb_size
        hybrid_nums = [None] * rb_size
        for i in range(rb_size):
            if rb_obj.modules[i].enable_check.isChecked():
                modules[i] = rb_obj.modules[i].module_id_inputbox.text()
                bias_volts[i] = abs(int(rb_obj.modules[i].bias_input.text()))
                # keep track of sensor type and number of hybrids on module for setting current compliance
                sensor_types[i] = rb_obj.modules[i].sensor.currentText()
                hybrid_nums[i] = abs(int(rb_obj.modules[i].sensor_num.currentText()))
        

        self.session = Session(
            rb=rb,
            rb_size=rb_size,
            rb_serial_number=rb_serial_number,
            modules=modules,
            kcu_ipaddress=kcu_ip,
            bias_volts=bias_volts,
            sensor_types=sensor_types,
            hybrid_nums=hybrid_nums
        )

        self.daq_stop_evt = threading.Event()

        self.daq_stop_evt.clear()
        self.daq_thread = threading.Thread(target=self.run_tests, args=(rb_obj,modules,))
        self.daq_thread.start()
        rb_obj.test_btn.setEnabled(False)
        rb_obj.kill_test_btn.setEnabled(True)
    
    def kill_thread(self, rb_obj):
        if self.daq_stop_evt:
            self.daq_stop_evt.set()
    
    def run_tests(self, rb_obj, modules):
        abort = False
        try:
            print(f"Running tests on RB{rb_obj.rb_pos}")
            rb_tests_str = rb_obj.scroll_container.getCheckedItems()
            rb_tests = []
            # Convert string to etlup test object
            for i in range(len(rb_tests_str)):
                rb_tests.append(rb_obj.rb_str_to_tests[rb_tests_str[i]])

            for i in range(len(modules)):
                if abort:
                    break
                if modules[i] is None:
                    continue

                mod_tests_str = rb_obj.modules[i].scroll_container.getCheckedItems()

                mod_tests = []
                for j in range(len(mod_tests_str)):
                    temp_tests = rb_obj.modules[i].module_str_to_tests[mod_tests_str[j]]
                    mod_tests += temp_tests

                test_sequence_str = rb_tests_str + mod_tests_str
                test_sequence = rb_tests + mod_tests

                print(f"Slot {i+1} Tests: {test_sequence_str}")
                print("Starting test sequence...")
                for test, result in self.session.iter_test_sequence(test_sequence, slot=i):
                    if self.daq_stop_evt.is_set():
                        abort = True
                        print("E-stop pressed, aborting")
                        break
                    if test.model in rb_obj.rb_tests_to_str:
                        test_str = rb_obj.rb_tests_to_str[test.model]
                    else:
                        test_str = rb_obj.modules[i].module_tests_to_str[test.model]
                    if isinstance(result, Exception):
                        print(f"{test_str} test failed: {result}")
                    else:
                        print(f"{test_str} test passed")
        except Exception as e:
            print(f"Test thread crashed: {e}")
        finally:
            self.finish_tests_signal.emit(rb_obj)


    def finish_tests(self, rb_obj):
        self.daq_thread = None
        self.daq_stop_evt = None

        rb_obj.test_btn.setEnabled(True)
        rb_obj.kill_test_btn.setEnabled(False)