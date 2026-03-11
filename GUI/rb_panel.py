import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from panel import Panel
from module_panel import ModulePanel

class RBPanel(Panel):
    def __init__(self, rb_pos):
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

        self.slot1 = ModulePanel(1)
        self.slot2 = ModulePanel(2)
        self.slot3 = ModulePanel(3)

        self.slot_row = QHBoxLayout()
        self.slot_row.addWidget(self.slot1)
        self.slot_row.addWidget(self.slot2)
        self.slot_row.addWidget(self.slot3)

        self.run_all_slot_tests = QPushButton("Run All Tests")
        self.run_all_slot_tests.setObjectName("redButton")
        self.slot_button_row = QHBoxLayout()
        self.slot_button_row.addStretch()
        self.slot_button_row.addWidget(self.run_all_slot_tests)
        self.slot_button_row.addStretch()

        main_layout.addLayout(self.slot_row)
        main_layout.addLayout(self.slot_button_row)


        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)