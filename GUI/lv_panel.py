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
from drivers.LV.lv_driver import LVPowerSupply

class LVPanel(Panel):

    update_GUI_signal = pyqtSignal(dict)
    def __init__(self, title="LV Supply"):
        super().__init__(title)
        
        self.setObjectName("LVPanel")

        self.lv_stop_evt = None
        self.lv_thread = None
        self.log_status = False
        self.log_timestamp = None

        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setObjectName("greenButton")
        self.btn_connect.clicked.connect(self.start_lv)
        self.btn_connect.setEnabled(True)
        self.btn_connect.setVisible(True)

        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setObjectName("redButton")
        self.btn_disconnect.clicked.connect(self.stop_lv)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setVisible(False)

        self.lbl_status = QLabel("Disconnected")

        self.btn_logging = QPushButton("Toggle Logging")
        self.btn_logging.setObjectName("blueButton")
        self.btn_logging.clicked.connect(self.toggle_log)
        self.lbl_logging = QLabel("Not Logging")
        self.lbl_logging.setEnabled(False)
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
        
        channel_row = QHBoxLayout()
        self.lbl_channel = make_label("OUTPUT: ---")
        self.lbl_channel.setEnabled(False)
        channel_row.addWidget(self.lbl_channel)

        set_label_row = QHBoxLayout()
        self.lbl_set_voltage = make_label("VSET: --- V")
        self.lbl_set_current = make_label("ISET: ---.- uA")
        self.lbl_set_current.setEnabled(False)
        self.lbl_set_voltage.setEnabled(False)
        set_label_row.addWidget(self.lbl_set_voltage)
        set_label_row.addWidget(self.lbl_set_current)

        mon_label_row = QHBoxLayout()
        self.lbl_mon_voltage = make_label("VMON: --- V")
        self.lbl_mon_current = make_label("IMON: ---.- uA")
        self.lbl_mon_current.setEnabled(False)
        self.lbl_mon_voltage.setEnabled(False)
        mon_label_row.addWidget(self.lbl_mon_voltage)
        mon_label_row.addWidget(self.lbl_mon_current)

        input_row = QHBoxLayout()

        channel_input_row = QHBoxLayout()
        voltage_input_row = QHBoxLayout()
        current_input_row = QHBoxLayout()

        self.btn_channel_on = QPushButton("OUTPUT ON")
        self.btn_channel_off = QPushButton("OUTPUT OFF")
        self.btn_channel_on.setObjectName("greenButton")
        self.btn_channel_off.setObjectName("redButton")
        self.btn_channel_on.clicked.connect(self.set_channel)
        self.btn_channel_off.clicked.connect(self.set_channel)
        self.btn_channel_off.setEnabled(False)
        self.btn_channel_on.setEnabled(False)
        channel_input_row.addWidget(self.btn_channel_on)
        channel_input_row.addWidget(self.btn_channel_off)

        self.lbl_set_voltage_field = make_label("Set Voltage (V): ")
        self.lbl_set_voltage_field.setEnabled(False)
        self.set_voltage_field = QLineEdit(parent=self)
        self.set_voltage_field.setFixedSize(60,25)
        self.btn_vset = QPushButton("Set")
        self.btn_vset.setObjectName("blueButton")
        self.btn_vset.clicked.connect(self.set_voltage)
        self.btn_vset.setEnabled(False)

        self.lbl_set_current_field = make_label("Set Current Limit (A):" )
        self.lbl_set_current_field.setEnabled(False)
        self.set_current_field = QLineEdit(parent=self)
        self.set_current_field.setFixedSize(60,25)
        self.btn_iset = QPushButton("Set")
        self.btn_iset.setObjectName("blueButton")
        self.btn_iset.clicked.connect(self.set_current)
        self.btn_iset.setEnabled(False)

        self.set_current_field.setEnabled(False)
        self.set_voltage_field.setEnabled(False)


        voltage_input_row.addWidget(self.lbl_set_voltage_field)
        voltage_input_row.addWidget(self.set_voltage_field)
        voltage_input_row.addWidget(self.btn_vset)
        current_input_row.addWidget(self.lbl_set_current_field)
        current_input_row.addWidget(self.set_current_field)
        current_input_row.addWidget(self.btn_iset)

        
        input_row.addLayout(channel_input_row)
        input_row.addStretch(1)
        input_row.addLayout(voltage_input_row)
        input_row.addStretch(1)
        input_row.addLayout(current_input_row)
        input_row.addStretch(1)


        main_layout = QVBoxLayout()
        main_layout.addLayout(button_row)
        main_layout.addLayout(channel_row)
        main_layout.addLayout(set_label_row)
        main_layout.addLayout(mon_label_row)
        main_layout.addLayout(input_row)



        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)
        self.sample_time = 0.5

        self.data = {}
        self.update_GUI_signal.connect(self.update_GUI)
        self.cmd_lock = threading.Lock()
        self.cmd_waiting = False
        self.cmd = None



    def update_GUI(self, data):
        if data["output"]:
            self.lbl_channel.setText("OUTPUT: ON")
            self.btn_channel_off.setEnabled(True)
            self.btn_channel_on.setEnabled(False)
        else:
            self.lbl_channel.setText("OUTPUT: OFF")
            self.btn_channel_off.setEnabled(False)
            self.btn_channel_on.setEnabled(True)

        self.lbl_set_voltage.setText(f"VSET: {data['vset']} V")
        self.lbl_set_current.setText(f"ISET: {data['iset']} A")
        self.lbl_mon_voltage.setText(f"VMON: {data['vmon']} V")
        self.lbl_mon_current.setText(f"IMON: {data['imon']} A")



    def start_lv(self):
        if self.lv_thread != None:
            print("LV thread already running")
            return
        
        self.lv_stop_evt = threading.Event()
        try:
            # TODO: Add more channels
            self.lv = LVPowerSupply("192.168.0.30", channel=1)
            self.lbl_status.setText("Connected")
            self.lv_stop_evt.clear()
            self.lv_thread = threading.Thread(target=self.lv_run, daemon=True)
            self.lv_thread.start()
            self.btn_disconnect.setEnabled(True)
            self.btn_disconnect.setVisible(True)
            self.btn_connect.setEnabled(False)
            self.btn_connect.setVisible(False)
            self.btn_channel_off.setEnabled(True)
            self.btn_channel_on.setEnabled(True)
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
            self.lbl_channel.setEnabled(True)
            self.lbl_mon_current.setEnabled(True)
            self.lbl_mon_voltage.setEnabled(True)
            time.sleep(self.sample_time)
        except Exception as e:
            print(f"Connection failed: {e}")
   
    def stop_lv(self):
        if self.lv_thread == None:
            print("LV thread not running")
            return
        
        self.lv_stop_evt.set()
        if self.lv_thread:
            self.lv_thread = None
        if self.lv:
            self.lv.close()
            self.lbl_status.setText("Disconnected")
            self.lbl_set_voltage.setText("VSET: --- V")
            self.lbl_set_current.setText("ISET: ---.- A")
            self.lbl_mon_voltage.setText("VMON: --- V")
            self.lbl_mon_current.setText("IMON: ---.- A")
            self.lbl_channel.setText("OUTPUT: ---")
            self.btn_disconnect.setEnabled(False)
            self.btn_disconnect.setVisible(False)
            self.btn_connect.setEnabled(True)
            self.btn_connect.setVisible(True)
            self.btn_channel_off.setEnabled(False)
            self.btn_channel_on.setEnabled(False)
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
            self.lbl_channel.setEnabled(False)
            self.lbl_mon_current.setEnabled(False)
            self.lbl_mon_voltage.setEnabled(False)


    def lv_run(self):
        while not self.lv_stop_evt.is_set():
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
                        self.lv.set_voltage(value)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd[0] == "iset":
                    try:
                        value = cmd[1]
                        self.lv.set_current_limit(value)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd[0] == "channel":
                    if self.output:
                        self.lv.set_channel_off()
                    else:
                        self.lv.set_channel_on()

            self.vset = self.lv.read_vset()
            self.vmon = self.lv.read_vmon()
            self.iset = self.lv.read_iset()
            self.imon = self.lv.read_imon()
            self.status = self.lv.read_status()
            self.output = self.status & 2**4

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

                resultdir = maindir / "Environmental Data" / "LV Supply Data"
                if not os.path.isdir(resultdir):
                    os.makedirs(resultdir)

                resultdir.mkdir(exist_ok=True)

                outfile = resultdir / f"LV_supply_data_{self.log_timestamp}.csv"

                data = {"OUTPUT": self.output, "VSET": self.vset, "VMON": self.vmon, "ISET": self.iset, "IMON": self.imon, "Status": self.status}
                with open(outfile, 'a') as f:
                    f.write(f"{timestamp}: {data}\n")

            time.sleep(self.sample_time)

    def set_voltage(self):
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
        with self.cmd_lock:
            self.cmd_waiting = True
            self.cmd = ["channel"]

    def toggle_log(self):
        self.log_status = not self.log_status
        if self.log_status:
            self.lbl_logging.setText("Logging")
            self.log_timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            self.lbl_logging.setText("Not Logging")