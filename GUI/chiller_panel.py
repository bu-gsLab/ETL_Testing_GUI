import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .panel import Panel
from drivers.Chiller.chiller_driver import Chiller

class ChillerPanel(Panel):
    update_GUI_signal = pyqtSignal(dict)
    def __init__(self, title="Chiller"):
        super().__init__(title)

        self.setObjectName("ChillerPanel")

        self.chiller_stop_evt = None
        self.chiller_thread = None
        self.log_status = False
        self.log_timestamp = None

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setObjectName("greenButton")
        self.btn_connect.clicked.connect(self.start_chiller)
        self.btn_connect.setEnabled(True)
        self.btn_connect.setVisible(True)

        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setObjectName("redButton")
        self.btn_disconnect.clicked.connect(self.stop_chiller)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setVisible(False)

        self.lbl_status = QLabel("Disconnected")

        self.btn_logging = QPushButton("Toggle Logging")
        self.btn_logging.setObjectName("blueButton")
        self.btn_logging.clicked.connect(self.toggle_log)
        self.lbl_logging = QLabel("Not Logging")
        self.btn_logging.setEnabled(False)

        button_row = QHBoxLayout()
        button_row.addWidget(self.btn_connect)
        button_row.addWidget(self.btn_disconnect)
        button_row.addWidget(self.lbl_status, 1, Qt.AlignLeft)
        button_row.addStretch(1)
        button_row.addWidget(self.btn_logging)
        button_row.addWidget(self.lbl_logging, 1, Qt.AlignLeft)

        def make_label(text):
            lbl = QLabel(text)
            #lbl.setFont(QFont("Calibri", 12))
            return lbl
        
        label_row = QHBoxLayout()

        self.lbl_power = make_label("Power: ---")
        self.lbl_set_temp = make_label("Set Temp: --- °C")
        self.lbl_curr_temp = make_label("Current Temp: --- °C")

        label_row.addWidget(self.lbl_power)
        label_row.addWidget(self.lbl_set_temp)
        label_row.addWidget(self.lbl_curr_temp)

        input_row = QHBoxLayout()

        self.lbl_power_toggle = make_label("Power: ")
        self.btn_power_on = QPushButton("ON")
        self.btn_power_on.setObjectName("greenButton")
        self.btn_power_on.clicked.connect(self.power_on)
        self.btn_power_off = QPushButton("OFF")
        self.btn_power_off.setObjectName("redButton")
        self.btn_power_off.clicked.connect(self.power_off)
        self.btn_power_on.setEnabled(False)
        self.btn_power_off.setEnabled(False)
        self.lbl_set_temp_input = make_label("Set Temp (°C): ")
        self.input_set_temp = QLineEdit()
        self.input_set_temp.setFixedSize(60, 25)
        self.input_set_temp.setEnabled(False)
        self.btn_set_temp = QPushButton("Set")
        self.btn_set_temp.setObjectName("blueButton")
        self.btn_set_temp.clicked.connect(self.set_temperature)
        self.btn_set_temp.setEnabled(False)
        input_row.addWidget(self.lbl_power_toggle)
        input_row.addWidget(self.btn_power_on)
        input_row.addWidget(self.btn_power_off)
        input_row.addStretch(1)
        input_row.addWidget(self.lbl_set_temp_input)
        input_row.addWidget(self.input_set_temp)
        input_row.addWidget(self.btn_set_temp)
        input_row.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(button_row)
        layout.addLayout(label_row)
        layout.addLayout(input_row)
        layout.addStretch(1)

        self.subgrid.addLayout(layout, 1, 0, 5, 3)
        self.sample_time = 1.0

        self.data = {}
        self.update_GUI_signal.connect(self.update_GUI)
        self.cmd_lock = threading.Lock()
        self.cmd_waiting = False
        self.cmd = None

        self.lbl_logging.setEnabled(False)
        self.lbl_curr_temp.setEnabled(False)
        self.lbl_power.setEnabled(False)
        self.lbl_power_toggle.setEnabled(False)
        self.lbl_set_temp_input.setEnabled(False)
        self.lbl_set_temp.setEnabled(False)

    def start_chiller(self):
        if self.chiller_thread != None:
            print("Chiller thread already running")
            return
        
        self.chiller_stop_evt = threading.Event()
        try:
            self.chiller = Chiller("/dev/chiller", baud=4800)
            self.lbl_status.setText("Connected")
            time.sleep(self.sample_time)
            self.chiller_stop_evt.clear()
            self.chiller_thread = threading.Thread(target=self.chiller_run, daemon=True)
            self.chiller_thread.start()
            self.btn_disconnect.setEnabled(True)
            self.btn_disconnect.setVisible(True)
            self.btn_connect.setEnabled(False)
            self.btn_connect.setVisible(False)
            self.btn_logging.setEnabled(True)
            self.btn_set_temp.setEnabled(True)
            self.input_set_temp.setEnabled(True)
            self.lbl_logging.setEnabled(True)
            self.lbl_curr_temp.setEnabled(True)
            self.lbl_power.setEnabled(True)
            self.lbl_power_toggle.setEnabled(True)
            self.lbl_set_temp_input.setEnabled(True)
            self.lbl_set_temp.setEnabled(True)

        except serial.SerialException as e:
            print(f"Failed to connect: {e}")
    
    
    def stop_chiller(self):
        time.sleep(self.sample_time)
        if self.chiller_thread == None:
            print("Chiller thread not running")
            return
        
        self.chiller_stop_evt.set()
        if self.chiller_thread:
            self.chiller_thread = None
        if self.chiller:
            self.chiller.close()
        self.lbl_status.setText("Disconnected")
        self.lbl_power.setText("Power: ---")
        self.lbl_set_temp.setText("Set Temp: --- °C")
        self.lbl_curr_temp.setText("Current Temp: --- °C")
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setVisible(False)
        self.btn_connect.setEnabled(True)
        self.btn_connect.setVisible(True)
        self.btn_logging.setEnabled(False)
        self.btn_set_temp.setEnabled(False)
        self.input_set_temp.setEnabled(False)
        self.lbl_logging.setEnabled(False)
        self.lbl_curr_temp.setEnabled(False)
        self.lbl_power.setEnabled(False)
        self.lbl_power_toggle.setEnabled(False)
        self.lbl_set_temp_input.setEnabled(False)
        self.lbl_set_temp.setEnabled(False)

    def power_on(self):
        with self.cmd_lock:
            self.cmd = ["power_on"]
            self.cmd_waiting = True

    def power_off(self):
        with self.cmd_lock:
            self.cmd = ["power_off"]
            self.cmd_waiting = True
        
    def set_temperature(self):
        try:
            value = float(self.input_set_temp.text())
        except ValueError:
            print("Invalid set temperature")
            return
        
        with self.cmd_lock:
            self.cmd_waiting = True
            self.cmd = ["set_temp", value]
        self.input_set_temp.clear()

    def update_GUI(self, data):
        self.lbl_curr_temp.setText(f"Current Temp: {data['curr_temp']:.2f} °C")
        self.lbl_set_temp.setText(f"Set Temp: {data['set_temp']:.2f} °C")
        if data["power"] == '1':
            self.lbl_power.setText("Power: ON")
            self.btn_power_on.setEnabled(False)
            self.btn_power_off.setEnabled(True)
        else:
            self.lbl_power.setText("Power: OFF")
            self.btn_power_on.setEnabled(True)
            self.btn_power_off.setEnabled(False)


    def chiller_run(self):
        while not self.chiller_stop_evt.is_set():
            with self.cmd_lock:
                cmd = self.cmd
                waiting = self.cmd_waiting
                if waiting:
                    self.cmd_waiting = False
                    self.cmd = None

            if waiting:
                if cmd[0] == "set_temp":
                    try:
                        value = cmd[1]
                        self.chiller.set_work_temperature(value)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd[0] == "power_on":
                    try:
                        self.chiller.set_power_on()
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd[0] == "power_off":
                    try:
                        self.chiller.set_power_off()
                    except Exception as e:
                        print(f"Error: {e}")
    
            try:
                self.curr_temp = self.chiller.get_temperature()
                self.set_temp = self.chiller.get_work_temperature()
                self.power = self.chiller.get_power().strip()

                self.data["curr_temp"] = self.curr_temp
                self.data["set_temp"] = self.set_temp
                self.data["power"] = self.power
            except Exception as e:
                print(f"Error reading chiller data: {e}")

            if self.data:
                self.update_GUI_signal.emit(self.data)

            if self.log_status:
                timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
                maindir = Path(__file__).parent.parent

                resultdir = maindir / "Environmental Data" / "Chiller Data"
                if not os.path.isdir(resultdir):
                    os.makedirs(resultdir)

                resultdir.mkdir(exist_ok=True)

                outfile = resultdir / f"chiller_data_{self.log_timestamp}.csv"

                data = {"Power": self.power.strip(), "Set Temp (°C)": self.set_temp, "Curr Temp (°C)": self.curr_temp}
                with open(outfile, 'a') as f:
                    f.write(f"{timestamp}: {data}\n")

            time.sleep(self.sample_time)

    def toggle_log(self):
        self.log_status = not self.log_status
        if self.log_status:
            self.lbl_logging.setText("Logging")
            self.log_timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            self.lbl_logging.setText("Not Logging")