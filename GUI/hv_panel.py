import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import (QPushButton, QLabel, QLineEdit, QHBoxLayout,
                             QVBoxLayout, QComboBox, QCheckBox, QMessageBox,
                             QInputDialog)
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .panel import Panel
from drivers.HV.hv_driver import HVPowerSupply

class HVPanel(Panel):
    update_GUI_signal = pyqtSignal(dict)
    iv_finished_signal = pyqtSignal(dict)
    iv_failed_signal = pyqtSignal(str)

    def __init__(self, title="HV Supply"):
        super().__init__(title)

        self.setObjectName("HVPanel")

        self.hv_stop_evt = None
        self.hv_thread = None
        self.log_status = False
        self.log_timestamp = None
        self.iv_running = False
        self.iv_abort_evt = threading.Event()
        self.preserve_output_on_abort_evt = threading.Event()

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setObjectName("neutralButton")
        self.btn_connect.clicked.connect(self.start_hv)
        self.btn_connect.setEnabled(True)
        self.btn_connect.setVisible(True)

        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setObjectName("neutralButton")
        self.btn_disconnect.clicked.connect(self.stop_hv)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setVisible(False)

        self.lbl_status = QLabel("Disconnected")
        self.lbl_status.setStyleSheet("color: #e53935;")

        self.channel_combobox = QComboBox()
        self.channel_combobox.addItems(["CH0", "CH1", "CH2", "CH3"])
        self.channel_combobox.setFixedWidth(100)
        
        self.btn_logging = QPushButton("Toggle Logging")
        self.btn_logging.setObjectName("neutralButton")
        self.btn_logging.clicked.connect(self.toggle_log)
        self.lbl_logging = QLabel("Not Logging")
        self.btn_logging.setEnabled(False)

        button_row = QHBoxLayout()
        button_row.setSpacing(round(self.em * 0.5))
        button_row.addWidget(self.btn_connect)
        button_row.addWidget(self.btn_disconnect)
        button_row.addWidget(self.lbl_status, 0, Qt.AlignLeft)
        button_row.addStretch(1)
        button_row.addWidget(self.channel_combobox)
        self.channel_combobox.setEnabled(False)
        button_row.addStretch(1)
        button_row.addWidget(self.btn_logging)
        button_row.addWidget(self.lbl_logging, 0, Qt.AlignLeft)
        
        set_label_row = QHBoxLayout()
        set_label_row.setSpacing(round(self.em * 0.5))
        self.lbl_set_voltage = QLabel("VSET: --- V")
        self.lbl_set_current = QLabel("ISET: ---.- uA")
        set_label_row.addWidget(self.lbl_set_voltage)
        set_label_row.addWidget(self.lbl_set_current)

        mon_label_row = QHBoxLayout()
        mon_label_row.setSpacing(round(self.em * 0.5))
        self.lbl_mon_voltage = QLabel("VMON: --- V")
        self.lbl_mon_current = QLabel("IMON: ---.- uA")
        mon_label_row.addWidget(self.lbl_mon_voltage)
        mon_label_row.addWidget(self.lbl_mon_current)

        input_row = QHBoxLayout()
        input_row.setSpacing(round(self.em * 0.5))

        channel_input_row = QHBoxLayout()
        voltage_input_row = QHBoxLayout()
        current_input_row = QHBoxLayout()
        for row in (channel_input_row, voltage_input_row, current_input_row):
            row.setSpacing(round(self.em * 0.5))

        self.btn_power = QPushButton("Power")
        self.btn_power.setObjectName("neutralButton")
        self.btn_power.clicked.connect(self.set_channel)
        self.btn_power.setEnabled(False)
        self.lbl_power = QLabel("---")
        self.lbl_power.setEnabled(False)
        channel_input_row.addWidget(self.btn_power)
        channel_input_row.addWidget(self.lbl_power)

        self.lbl_set_voltage_field = QLabel("Set Voltage (V): ")
        self.set_voltage_field = QLineEdit(parent=self)
        self.set_voltage_field.setFixedWidth(60)
        self.set_voltage_field.setEnabled(False)
        self.btn_vset = QPushButton("Set")
        self.btn_vset.setObjectName("neutralButton")
        self.btn_vset.clicked.connect(self.set_voltage)
        self.btn_vset.setEnabled(False)

        self.lbl_set_current_field = QLabel("Set Current Limit (uA):" )
        self.set_current_field = QLineEdit(parent=self)
        self.set_current_field.setFixedWidth(60)
        self.set_current_field.setEnabled(False)
        self.btn_iset = QPushButton("Set")
        self.btn_iset.setObjectName("neutralButton")
        self.btn_iset.clicked.connect(self.set_current)
        self.btn_iset.setEnabled(False)


        voltage_input_row.addWidget(self.lbl_set_voltage_field)
        voltage_input_row.addWidget(self.set_voltage_field)
        voltage_input_row.addWidget(self.btn_vset)
        current_input_row.addWidget(self.lbl_set_current_field)
        current_input_row.addWidget(self.set_current_field)
        current_input_row.addWidget(self.btn_iset)

        
        input_row.addLayout(channel_input_row)
        input_row.addSpacing(self.em*2)
        input_row.addStretch(1)

        iv_row = QHBoxLayout()
        iv_row.setSpacing(round(self.em * 0.5))
        self.iv_fields = {}
        self.iv_labels = []
        for key, label, default in (
            ("moduleid", "Module ID:", ""),
            ("start_v", "Start (V):", "0"),
            ("stop_v", "Stop (V):", "100"),
            ("step_v", "Step (V):", "5"),
            ("curr_limit", "Limit (uA):", "45"),
            ("delay", "Delay (s):", "3"),
        ):
            field_label = QLabel(label)
            field_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.iv_labels.append(field_label)
            iv_row.addWidget(field_label, 0, Qt.AlignVCenter)
            field = QLineEdit(default, parent=self)
            field.setFixedWidth(60 if key != "moduleid" else 90)
            field.setAlignment(Qt.AlignCenter)
            field.setEnabled(False)
            self.iv_fields[key] = field
            iv_row.addWidget(field, 0, Qt.AlignVCenter)
        self.iv_leave_on = QCheckBox("Leave on")
        self.iv_leave_on.setEnabled(False)
        self.btn_iv_curve = QPushButton("Run IV Curve")
        self.btn_iv_curve.setObjectName("neutralButton")
        self.btn_iv_curve.setEnabled(False)
        self.btn_iv_curve.clicked.connect(self.run_iv_curve)
        self.lbl_iv_status = QLabel("Idle")
        iv_row.addWidget(self.iv_leave_on)
        iv_row.addWidget(self.btn_iv_curve)
        iv_row.addWidget(self.lbl_iv_status)
        input_row.addLayout(voltage_input_row)
        input_row.addSpacing(self.em*2)
        input_row.addStretch(1)
        input_row.addLayout(current_input_row)
        input_row.addStretch(1)


        main_layout = QVBoxLayout()
        main_layout.setSpacing(round(self.em * 0.5))
        main_layout.addLayout(button_row)
        main_layout.addLayout(set_label_row)
        main_layout.addLayout(mon_label_row)
        main_layout.addLayout(input_row)
        main_layout.addLayout(iv_row)

        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)
        self.sample_time = 0.5

        self.cmd_lock = threading.Lock()
        self.cmd_waiting = False
        self.cmd = None

        self.data = {}

        self.update_GUI_signal.connect(self.update_GUI)
        self.iv_finished_signal.connect(self.iv_finished)
        self.iv_failed_signal.connect(self.iv_failed)
        self.lbl_set_current_field.setEnabled(False)
        self.lbl_set_voltage_field.setEnabled(False)
        self.lbl_logging.setEnabled(False)
        self.lbl_set_current.setEnabled(False)
        self.lbl_set_voltage.setEnabled(False)
        self.lbl_mon_current.setEnabled(False)
        self.lbl_mon_voltage.setEnabled(False)
        self.lbl_iv_status.setEnabled(False)
        for label in self.iv_labels:
            label.setEnabled(False)
        self.ramp = None

    def start_hv(self):
        if self.hv_thread != None:
            print("HV thread already running")
            return
        
        self.hv_stop_evt = threading.Event()
        try:
            self.hv = HVPowerSupply("/dev/hv_supply", baud=9600, bd_addr=0, channel=self.channel_combobox.currentIndex())
            self.lbl_status.setText("Connected")
            self.lbl_status.setStyleSheet("color: #16a34a;")
            self.hv_stop_evt.clear()
            self.hv_thread = threading.Thread(target=self.hv_run, daemon=True)
            self.hv_thread.start()
            self.btn_disconnect.setEnabled(True)
            self.btn_disconnect.setVisible(True)
            self.channel_combobox.setEnabled(True)
            self.btn_connect.setEnabled(False)
            self.btn_connect.setVisible(False)
            self.btn_power.setEnabled(True)
            self.btn_iset.setEnabled(True)
            self.btn_vset.setEnabled(True)
            self.btn_logging.setEnabled(True)
            self.set_current_field.setEnabled(True)
            self.set_voltage_field.setEnabled(True)
            self.lbl_set_current_field.setEnabled(True)
            self.lbl_set_voltage_field.setEnabled(True)
            self.lbl_logging.setEnabled(True)
            self.lbl_set_current.setEnabled(True)
            self.lbl_set_voltage.setEnabled(True)
            self.lbl_power.setEnabled(True)
            self.lbl_mon_current.setEnabled(True)
            self.lbl_mon_voltage.setEnabled(True)
            self.set_iv_controls_enabled(True)
            time.sleep(self.sample_time)
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
    
   
    def stop_hv(self):
        self.stop_logging()
        if self.hv_thread == None:
            return True

        if self.iv_running:
            self.iv_abort_evt.set()
        self.hv_stop_evt.set()
        self.hv_thread.join()
        self.hv_stop_evt.clear()

        self.hv_thread = None
        if self.hv:
            self.hv.close()
            self.lbl_status.setText("Disconnected")
            self.lbl_status.setStyleSheet("color: #e53935;")
            self.lbl_set_voltage.setText("VSET: --- V")
            self.lbl_set_current.setText("ISET: ---.- uA")
            self.lbl_mon_voltage.setText("VMON: --- V")
            self.lbl_mon_current.setText("IMON: ---.- uA")
            self.lbl_power.setText("---")
            self.lbl_power.setStyleSheet("")
            self.btn_disconnect.setEnabled(False)
            self.btn_disconnect.setVisible(False)
            self.channel_combobox.setEnabled(False)
            self.btn_connect.setEnabled(True)
            self.btn_connect.setVisible(True)
            self.btn_power.setEnabled(False)
            self.btn_iset.setEnabled(False)
            self.btn_vset.setEnabled(False)
            self.btn_logging.setEnabled(False)
            self.set_current_field.setEnabled(False)
            self.set_voltage_field.setEnabled(False)
            self.lbl_set_current_field.setEnabled(False)
            self.lbl_set_voltage_field.setEnabled(False)
            self.lbl_logging.setEnabled(False)
            self.lbl_set_current.setEnabled(False)
            self.lbl_set_voltage.setEnabled(False)
            self.lbl_power.setEnabled(False)
            self.lbl_mon_current.setEnabled(False)
            self.lbl_mon_voltage.setEnabled(False)
            self.set_iv_controls_enabled(False)
        return True


    def hv_run(self):
        while not self.hv_stop_evt.is_set():

            with self.cmd_lock:
                cmd = self.cmd
                waiting = self.cmd_waiting
                if waiting:
                    self.cmd_waiting = False
                    self.cmd = None

            if waiting:
                if cmd[0] == "vset":
                    try:
                        value = cmd[1]
                        self.hv.set_voltage(value)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd[0] == "iset":
                    try:
                        value = cmd[1]
                        self.hv.set_current_limit(value)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd[0] == "output":
                    if self.output:
                        self.hv.set_channel_off()
                    else:
                        self.hv.set_channel_on()
                elif cmd[0] == "iv_curve":
                    try:
                        result = self.hv.plot_IV_curve(
                            **cmd[1], stop_event=self.iv_abort_evt,
                            progress_callback=self.update_GUI_signal.emit,
                            preserve_output_on_abort=self.preserve_output_on_abort_evt)
                        self.iv_finished_signal.emit(result)
                    except Exception as e:
                        self.iv_failed_signal.emit(str(e))
            self.hv.channel = self.channel_combobox.currentIndex()
            self.vset = self.hv.extract_float_value(self.hv.read_vset())
            self.vmon = self.hv.extract_float_value(self.hv.read_vmon())
            self.iset = self.hv.extract_float_value(self.hv.read_iset())
            self.imon = self.hv.extract_float_value(self.hv.read_imon())
            self.status = int(self.hv.read_status()['VAL'])
            self.output = self.status & 1
            if self.status & 2:
                self.ramp = "Ramp Up"
            elif self.status & 4:
                self.ramp = "Ramp Down"
            else:
                self.ramp = None

            self.data["vset"] = self.vset
            self.data["vmon"] = self.vmon
            self.data["iset"] = self.iset
            self.data["imon"] = self.imon
            self.data["status"] = self.status
            self.data["output"] = self.output

            self.update_GUI_signal.emit(self.data)

            if self.log_status:
                timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
                maindir = Path(__file__).parent.parent

                resultdir = maindir / "Environmental Data" / "HV Supply Data"
                if not os.path.isdir(resultdir):
                    os.makedirs(resultdir)

                resultdir.mkdir(exist_ok=True)

                outfile = resultdir / f"hv_supply_data_{self.log_timestamp}.csv"

                data = {"CH": self.hv.channel, "OUTPUT": self.output, "VSET": self.vset, "VMON": self.vmon, "ISET": self.iset, "IMON": self.imon, "Status": self.status}
                with open(outfile, 'a') as f:
                    f.write(f"{timestamp}: {data}\n")

            time.sleep(self.sample_time)

    def update_GUI(self, data):
        if self.hv_thread is None:
            return

        if data["status"] & 2:
            self.ramp = "Ramp Up"
        elif data["status"] & 4:
            self.ramp = "Ramp Down"
        else:
            self.ramp = None

        if data["output"]:
            if not self.ramp:
                self.lbl_power.setText("ON")
                self.lbl_power.setStyleSheet("color: #16a34a;")
            else:
                self.lbl_power.setText(self.ramp)
                self.lbl_power.setStyleSheet("color: #facc15")
        else:
            if not self.ramp:
                self.lbl_power.setText("OFF")
                self.lbl_power.setStyleSheet("color: #e53935;")
            else:
                self.lbl_power.setText(self.ramp)
                self.lbl_power.setStyleSheet("color: #facc15")


        self.lbl_set_voltage.setText(f"VSET: {data['vset']} V")
        self.lbl_set_current.setText(f"ISET: {data['iset']} uA")
        self.lbl_mon_voltage.setText(f"VMON: {data['vmon']} V")
        self.lbl_mon_current.setText(f"IMON: {data['imon']:.3f} uA")


    def set_voltage(self):
        if self.iv_running:
            QMessageBox.information(self, "IV curve running", "Abort the IV curve before changing VSET.")
            return
        try:
            value = float(self.set_voltage_field.text())
        except ValueError:
            print("Invalid set voltage")
            return

        with self.cmd_lock:
            self.cmd_waiting = True
            self.cmd = ["vset", value]
        self.set_voltage_field.clear()

    def set_current(self):
        if self.iv_running:
            QMessageBox.information(self, "IV curve running", "Abort the IV curve before changing ISET.")
            return
        try:
            value = float(self.set_current_field.text())
        except ValueError:
            print("Invalid set current")
            return
        
        with self.cmd_lock:
            self.cmd_waiting = True
            self.cmd = ["iset", value]
        self.set_current_field.clear()
    
    def set_channel(self):
        if self.iv_running:
            QMessageBox.information(self, "IV curve running", "Use Abort to stop the active IV curve safely.")
            return
        with self.cmd_lock:
            self.cmd_waiting = True
            self.cmd = ["output"]

    def toggle_log(self):
        self.log_status = not self.log_status
        if self.log_status:
            self.lbl_logging.setText("Logging")
            self.log_timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            self.lbl_logging.setText("Not Logging")

    def stop_logging(self):
        self.log_status = False
        self.log_timestamp = None
        self.lbl_logging.setText("Not Logging")

    def shutdown(self):
        """Stop GUI activity and disconnect without changing the HV state."""
        self.preserve_output_on_abort_evt.set()
        try:
            return self.stop_hv()
        finally:
            self.preserve_output_on_abort_evt.clear()

    def set_iv_controls_enabled(self, enabled):
        for label in self.iv_labels:
            label.setEnabled(enabled)
        for field in self.iv_fields.values():
            field.setEnabled(enabled)
        self.iv_leave_on.setEnabled(enabled)
        self.btn_iv_curve.setEnabled(enabled)
        self.lbl_iv_status.setEnabled(enabled)

    def set_manual_controls_enabled(self, enabled):
        for widget in (self.btn_disconnect, self.channel_combobox, self.btn_power,
                       self.btn_iset, self.btn_vset, self.btn_logging,
                       self.set_current_field, self.set_voltage_field):
            widget.setEnabled(enabled)

    def run_iv_curve(self):
        if self.iv_running:
            self.iv_abort_evt.set()
            self.btn_iv_curve.setEnabled(False)
            self.lbl_iv_status.setText("Aborting...")
            return

        try:
            moduleid = self.iv_fields["moduleid"].text().strip()
            if not moduleid:
                raise ValueError("Module ID is required")
            if moduleid in (".", "..") or any(char in moduleid for char in '<>:"/\\|?*'):
                raise ValueError("Module ID contains characters that cannot be used in a folder name")
            params = {
                "start_v": float(self.iv_fields["start_v"].text()),
                "stop_v": float(self.iv_fields["stop_v"].text()),
                "step_v": float(self.iv_fields["step_v"].text()),
                "curr_limit": float(self.iv_fields["curr_limit"].text()),
                "moduleid": moduleid,
                "leave_on": self.iv_leave_on.isChecked(),
                "delay": float(self.iv_fields["delay"].text()),
            }
            if params["step_v"] == 0:
                raise ValueError("Voltage step cannot be zero")
            if (params["stop_v"] - params["start_v"]) * params["step_v"] < 0:
                raise ValueError("Voltage step must point from start toward stop")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid IV settings", str(e))
            return

        comment, accepted = QInputDialog.getMultiLineText(
            self,
            "IV curve context",
            "Add context or comments for this run:",
        )
        if not accepted:
            return
        params["comment"] = comment

        with self.cmd_lock:
            if self.cmd_waiting:
                QMessageBox.warning(self, "HV busy", "Another HV command is pending.")
                return
            self.cmd_waiting = True
            self.cmd = ["iv_curve", params]
        self.iv_abort_evt.clear()
        self.iv_running = True
        for field in self.iv_fields.values():
            field.setEnabled(False)
        self.iv_leave_on.setEnabled(False)
        self.btn_iv_curve.setText("Abort")
        self.btn_iv_curve.setObjectName("redButton")
        self.btn_iv_curve.style().unpolish(self.btn_iv_curve)
        self.btn_iv_curve.style().polish(self.btn_iv_curve)
        self.lbl_iv_status.setText("Running...")

    def iv_finished(self, result):
        self.iv_running = False
        self.set_iv_controls_enabled(self.hv_thread is not None)
        self.reset_iv_button()
        self.lbl_iv_status.setText("Complete")
        QMessageBox.information(
            self, "IV curve complete",
            f"Saved run files to:\n{result['result_dir']}\n\n"
            f"Plot: {result['plot_path'].name}\n"
            f"Raw data: {result['csv_path'].name}\n"
            f"Comments: {result['comment_path'].name}")

    def iv_failed(self, message):
        was_aborted = self.iv_abort_evt.is_set()
        self.iv_running = False
        self.set_iv_controls_enabled(self.hv_thread is not None)
        self.reset_iv_button()
        if was_aborted:
            self.lbl_iv_status.setText("Aborted")
            QMessageBox.information(self, "IV curve aborted", "The IV curve was aborted and HV was turned off.")
        else:
            self.lbl_iv_status.setText("Failed")
            QMessageBox.critical(self, "IV curve failed", message)

    def reset_iv_button(self):
        self.iv_abort_evt.clear()
        self.btn_iv_curve.setText("Run IV Curve")
        self.btn_iv_curve.setObjectName("neutralButton")
        self.btn_iv_curve.setEnabled(self.hv_thread is not None)
        self.btn_iv_curve.style().unpolish(self.btn_iv_curve)
        self.btn_iv_curve.style().polish(self.btn_iv_curve)
