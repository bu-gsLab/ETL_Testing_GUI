import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QCheckBox, QScrollArea
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from panel import Panel
from module_panel import ModulePanel
from helpers.checkable_combobox import CheckableComboBox

class RBPanel(Panel):
    run_tests_signal = pyqtSignal(object)
    def __init__(self, rb_pos):
        self.rb_pos = rb_pos
        self.rb_size = 3
        super().__init__(f"RB {rb_pos}")
        self.setObjectName("RBPanel")
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

        main_layout = QVBoxLayout()

        self.rb_id_lbl = QLabel("RB Serial #: ")
        self.rb_id_field = QLineEdit()
        self.rb_id_field.setFixedSize(130,50)
        self.rb_id_row = QHBoxLayout()
        self.rb_id_row.addWidget(self.rb_id_lbl)
        self.rb_id_row.addWidget(self.rb_id_field)
        self.rb_id_row.addStretch()

        self.test_select_row = QHBoxLayout()
        container = QWidget()
        self.scroll_container = CheckableComboBox(container)

        self.scroll_container.addItem("Select tests...")
        self.scroll_container.model().item(0, 0).setFlags(Qt.NoItemFlags)
        self.scroll_container.view().setRowHidden(0, True)
        for i in range(30):
            self.scroll_container.addItem(f"Test {i+1}")
        
        self.test_select_lbl = QLabel("Tests: ")
        self.test_select_row.addWidget(self.test_select_lbl)
        self.test_select_row.addWidget(self.scroll_container)
        self.test_select_row.addStretch()

        self.slot1 = ModulePanel(1)
        self.slot2 = ModulePanel(2)
        self.slot3 = ModulePanel(3)
        self.modules = [self.slot1, self.slot2, self.slot3]

        self.slot_row = QHBoxLayout()
        self.slot_row.addWidget(self.slot1)
        self.slot_row.addWidget(self.slot2)
        self.slot_row.addWidget(self.slot3)

        self.test_btn = QPushButton("Run Tests")
        self.test_btn.clicked.connect(self.run_tests)
        self.test_btn.setObjectName("redButton")
        self.test_btn_row = QHBoxLayout()
        self.test_btn_row.addStretch()
        self.test_btn_row.addWidget(self.test_btn)
        self.test_btn_row.addStretch()

        main_layout.addLayout(self.rb_id_row)
        main_layout.addLayout(self.test_select_row)
        main_layout.addLayout(self.slot_row)
        main_layout.addLayout(self.test_btn_row)


        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)

    def run_tests(self):
        self.run_tests_signal.emit(self)