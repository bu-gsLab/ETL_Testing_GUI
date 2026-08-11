import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QFrame, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QCheckBox, QScrollArea, QWidget, QComboBox, QSizePolicy
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .panel import Panel
from .helpers.checkable_combobox import CheckableComboBox

from etlup.tamalero import *
from qaqc.tests.charge_injection import ChargeInjectionV0

class ModulePanel(Panel):
    def __init__(self, slot_no):
        super().__init__(f"Slot {slot_no}")
        self.slot_no = slot_no
        self.module_str_to_tests = {
            "Threshold Calibration": [
                Baseline.BaselineV0,
                Noisewidth.NoisewidthV0,
            ],
            "Charge Injection": [
                Baseline.BaselineV0,
                Noisewidth.NoisewidthV0,
                ChargeInjectionV0,
            ],
        }
        self.module_tests_to_str = {
            Baseline.BaselineV0: "Baseline",
            Noisewidth.NoisewidthV0: "Noise Width",
            ChargeInjectionV0: "Charge Injection",
        }

        self.setObjectName("ModulePanel")
        self.setMinimumWidth(135)
        self.setMaximumWidth(155)
        self.setFixedHeight(round(self.em * 14))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.subgrid.setContentsMargins(4, 4, 4, 4)
        self.subgrid.setSpacing(3)

        self.enable_check = QCheckBox("Use Slot", self)
        self.enable_check.setChecked(False)
        self.enable_check.stateChanged.connect(self.checkbox_changed)
        self.enable_check.setStyleSheet("QCheckBox { color: white; }") #
        
        self.module_id_row = QHBoxLayout()

        self.module_id_label = QLabel("ID:")
        self.module_id_inputbox = QLineEdit()
        self.module_id_inputbox.setFixedWidth(95)
        self.module_id_row.addWidget(self.module_id_label)
        self.module_id_row.addWidget(self.module_id_inputbox)
        self.module_id_row.addStretch()


        self.test_select_row = QVBoxLayout()
        self.test_select_row.setSpacing(1)
        container = QWidget()
        self.scroll_container = CheckableComboBox(container)
        self.scroll_container.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.scroll_container.setMinimumContentsLength(12)
        self.scroll_container.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )

        self.scroll_container.addItem("Select tests...")
        self.scroll_container.model().item(0, 0).setFlags(Qt.NoItemFlags)
        self.scroll_container.view().setRowHidden(0, True)
        for key in self.module_str_to_tests:
            self.scroll_container.addItem(key)
        popup_width = self.scroll_container.view().sizeHintForColumn(0) + 30
        self.scroll_container.view().setMinimumWidth(popup_width)
        
        self.test_select_lbl = QLabel("Tests:")
        self.test_select_row.addWidget(self.test_select_lbl)
        self.test_select_row.addWidget(self.scroll_container)
        
        self.sensor_row = QHBoxLayout()
        self.sensor_label = QLabel("Sensor:")
        self.sensor = QComboBox()
        self.sensor.addItems(["FBK", "HPK"])
        self.sensor.setFixedWidth(70)
        self.sensor_row.addWidget(self.sensor_label)
        self.sensor_row.addWidget(self.sensor)
        self.sensor_row.addStretch()

        self.sensor_num_row = QHBoxLayout()
        self.sensor_num_label = QLabel("Hybrids:")
        self.sensor_num = QComboBox()
        self.sensor_num.addItems(["1","2","3","4"])
        self.sensor_num.setFixedWidth(55)
        self.sensor_num_row.addWidget(self.sensor_num_label)
        self.sensor_num_row.addWidget(self.sensor_num)
        self.sensor_num_row.addStretch()

        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(3)
        details_layout.addLayout(self.module_id_row)
        details_layout.addLayout(self.test_select_row)
        details_layout.addLayout(self.sensor_row)
        details_layout.addLayout(self.sensor_num_row)
        self.details_widget.hide()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(3)
        main_layout.addWidget(self.enable_check)
        main_layout.addWidget(self.details_widget)
        main_layout.addStretch()

        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)

    def checkbox_changed(self):
        enabled = self.enable_check.isChecked()
        self.details_widget.setVisible(enabled)
