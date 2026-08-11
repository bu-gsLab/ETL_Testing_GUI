import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QSizePolicy
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .panel import Panel
from .module_panel import ModulePanel
from .helpers.checkable_combobox import CheckableComboBox

from etlup.tamalero import *

class RBPanel(Panel):
    run_tests_signal = pyqtSignal(object)
    kill_tests_signal = pyqtSignal(object)
    def __init__(self, rb_pos):
        self.rb_pos = rb_pos
        self.rb_size = 3
        super().__init__(f"RB {rb_pos}")

        self.rb_str_to_tests = {
            "RB Communication": ReadoutBoardCommunication.ReadoutBoardCommunicationV0
        }

        self.rb_tests_to_str = {
            ReadoutBoardCommunication.ReadoutBoardCommunicationV0: "RB Communication"
        }

        self.setObjectName("RBPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
    
        main_layout = QVBoxLayout()

        self.rb_id_lbl = QLabel("RB Serial #:")
        self.rb_id_field = QLineEdit()
        self.rb_id_field.setFixedWidth(130)

        self.rb_type_label = QLabel("Board Type:")
        self.rb_type = QComboBox()
        self.rb_type.addItems(["RB3", "RB6", "RB7"])

        self.bias_input_label = QLabel("Bias:")
        self.bias_input = QLineEdit("0")
        self.bias_input.setFixedWidth(50)

        container = QWidget()
        self.scroll_container = CheckableComboBox(container)
        self.scroll_container.setFixedWidth(175)

        self.scroll_container.addItem("Select tests...")
        self.scroll_container.model().item(0, 0).setFlags(Qt.NoItemFlags)
        self.scroll_container.view().setRowHidden(0, True)
        for key in self.rb_str_to_tests:
            self.scroll_container.addItem(key)
        
        self.test_select_lbl = QLabel("Tests:")

        self.rb_config_row = QHBoxLayout()
        self.rb_config_row.setSpacing(5)
        self.rb_config_row.addWidget(self.rb_id_lbl)
        self.rb_config_row.addWidget(self.rb_id_field)
        self.rb_config_row.addSpacing(12)
        self.rb_config_row.addWidget(self.rb_type_label)
        self.rb_config_row.addWidget(self.rb_type)
        self.rb_config_row.addSpacing(12)
        self.rb_config_row.addWidget(self.bias_input_label)
        self.rb_config_row.addWidget(self.bias_input)
        self.rb_config_row.addSpacing(12)
        self.rb_config_row.addWidget(self.test_select_lbl)
        self.rb_config_row.addWidget(self.scroll_container)
        self.rb_config_row.addStretch()

        self.slot_row = QHBoxLayout()
        self.slot_row.setContentsMargins(0, 0, 0, 0)
        self.slot_row.setSpacing(4)
        self.modules = []
        self.set_slot_count(self.rb_size)
        self.rb_type.currentTextChanged.connect(self.rb_type_changed)

        self.test_btn = QPushButton("Run Tests")
        self.test_btn.clicked.connect(self.run_tests)
        self.test_btn.setObjectName("greenButton")

        self.kill_test_btn = QPushButton("E-Stop")
        self.kill_test_btn.clicked.connect(self.kill_tests)
        self.kill_test_btn.setObjectName("redButton")
        self.kill_test_btn.setEnabled(False)

        self.test_btn_row = QHBoxLayout()
        self.test_btn_row.addStretch()
        self.test_btn_row.addWidget(self.test_btn)
        self.test_btn_row.addWidget(self.kill_test_btn)
        self.test_btn_row.addStretch()

        main_layout.addLayout(self.rb_config_row)
        main_layout.addLayout(self.slot_row)
        main_layout.addLayout(self.test_btn_row)


        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)

    def run_tests(self):
        self.run_tests_signal.emit(self)

    def kill_tests(self):
        self.kill_tests_signal.emit(self)

    def rb_type_changed(self, rb_type):
        self.set_slot_count(int(rb_type.removeprefix("RB")))

    def set_slot_count(self, slot_count):
        while self.slot_row.count():
            item = self.slot_row.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

        self.rb_size = slot_count
        self.modules = [ModulePanel(slot + 1) for slot in range(slot_count)]
        maximum_slot_width = {3: 280, 6: 155, 7: 135}[slot_count]
        for module in self.modules:
            module.setMaximumWidth(maximum_slot_width)
            self.slot_row.addWidget(module)
