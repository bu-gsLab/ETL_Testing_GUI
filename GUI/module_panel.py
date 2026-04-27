import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QFrame, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QCheckBox, QScrollArea, QWidget, QComboBox
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .panel import Panel
from .helpers.checkable_combobox import CheckableComboBox

from etlup.tamalero import *

class ModulePanel(Panel):
    def __init__(self, slot_no):
        super().__init__(f"Slot {slot_no}")
        self.slot_no = slot_no
        self.module_str_to_tests = {
            "Threshold": [Baseline.BaselineV0, Noisewidth.NoisewidthV0]
        }
        self.module_tests_to_str = {
            Baseline.BaselineV0: "Baseline",
            Noisewidth.NoisewidthV0: "Noise Width"
        }

        self.setObjectName("ModulePanel")
        self.enable_check = QCheckBox("Use Slot", self)
        self.enable_check.setChecked(False)
        self.enable_check.stateChanged.connect(self.checkbox_changed)
        self.enable_check.setStyleSheet("QCheckBox { color: white; }") #
        
        self.module_id_row = QHBoxLayout()

        self.module_id_label = QLabel("Module ID: ")
        self.module_id_inputbox = QLineEdit()
        self.module_id_inputbox.setEnabled(False)
        self.module_id_label.hide()
        self.module_id_inputbox.hide()
        self.module_id_inputbox.setFixedSize(100,25)
        self.module_id_row.addWidget(self.module_id_label)
        self.module_id_row.addWidget(self.module_id_inputbox)
        self.module_id_row.addStretch()


        self.test_select_row = QHBoxLayout()
        container = QWidget()
        self.scroll_container = CheckableComboBox(container)

        self.scroll_container.addItem("Select tests...")
        self.scroll_container.model().item(0, 0).setFlags(Qt.NoItemFlags)
        self.scroll_container.view().setRowHidden(0, True)
        for key in self.module_str_to_tests:
            self.scroll_container.addItem(key)
        
        self.test_select_lbl = QLabel("Tests: ")
        self.test_select_row.addWidget(self.test_select_lbl)
        self.test_select_row.addWidget(self.scroll_container)
        self.test_select_lbl.hide()
        self.scroll_container.hide()
        self.test_select_row.addStretch()
        
        self.bias_input_row = QHBoxLayout()
        self.bias_input_label = QLabel("Bias: ")
        self.bias_input = QLineEdit()
        self.bias_input.setText("0")
        self.bias_input.setEnabled(False)
        self.bias_input_label.hide()
        self.bias_input.hide()
        self.bias_input.setFixedSize(50,23)
        self.bias_input_row.addWidget(self.bias_input_label)
        self.bias_input_row.addWidget(self.bias_input)
        self.bias_input_row.addStretch()

        self.sensor_row = QHBoxLayout()
        self.sensor_label = QLabel("Sensor Type: ")
        self.sensor = QComboBox()
        self.sensor.addItems(["FBK", "HPK"])
        self.sensor_label.hide()
        self.sensor.hide()
        self.sensor_row.addWidget(self.sensor_label)
        self.sensor_row.addWidget(self.sensor)
        self.sensor_row.addStretch()

        self.sensor_num_row = QHBoxLayout()
        self.sensor_num_label = QLabel("# of Hybrids: ")
        self.sensor_num = QComboBox()
        self.sensor_num.addItems(["1","2","3","4"])
        self.sensor_num_label.hide()
        self.sensor_num.hide()
        self.sensor_num_row.addWidget(self.sensor_num_label)
        self.sensor_num_row.addWidget(self.sensor_num)
        self.sensor_num_row.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.enable_check)
        main_layout.addLayout(self.module_id_row)
        main_layout.addLayout(self.test_select_row)
        main_layout.addLayout(self.bias_input_row)
        main_layout.addLayout(self.sensor_row)
        main_layout.addLayout(self.sensor_num_row)
        main_layout.addStretch()

        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)

    def checkbox_changed(self):
        if self.enable_check.isChecked() == True:
            self.module_id_inputbox.setEnabled(True)
            self.module_id_label.show()
            self.module_id_inputbox.show()
            self.test_select_lbl.show()
            self.scroll_container.show()
            self.bias_input_label.show()
            self.bias_input.show()
            self.bias_input.setEnabled(True)
            self.sensor_label.show()
            self.sensor.show()
            self.sensor_num_label.show()
            self.sensor_num.show()
        else:
            self.module_id_inputbox.setEnabled(False)
            self.module_id_label.hide()
            self.module_id_inputbox.hide()
            self.test_select_lbl.hide()
            self.scroll_container.hide()
            self.bias_input_label.hide()
            self.bias_input.hide()
            self.bias_input.setEnabled(False)
            self.sensor_label.hide()
            self.sensor.hide()
            self.sensor_num_label.hide()
            self.sensor_num.hide()