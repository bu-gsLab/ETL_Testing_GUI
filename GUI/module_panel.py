import sys
import threading
import serial
import time
import os

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QCheckBox, QScrollArea, QWidget
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from panel import Panel

class ModulePanel(Panel):
    def __init__(self, slot_no):
        super().__init__(f"Slot {slot_no}")
        self.setObjectName("ModulePanel")
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

        self.enable_check = QCheckBox("Use Slot", self)
        self.enable_check.setChecked(False)
        self.enable_check.stateChanged.connect(self.checkbox_changed)
        self.enable_check.setStyleSheet("QCheckBox { color: white; }") #
        
        self.module_id_row = QHBoxLayout()

        self.module_id_label = QLabel("Module ID: ")
        self.module_id_label.setFont(QFont("Calibri", 12))
        self.module_id_inputbox = QLineEdit()
        self.module_id_inputbox.setEnabled(False)
        self.module_id_label.hide()
        self.module_id_inputbox.hide()
        self.module_id_inputbox.setFixedSize(100,50)
        self.module_id_row.addWidget(self.module_id_label)
        self.module_id_row.addWidget(self.module_id_inputbox)
        self.module_id_row.addStretch()


        self.test_select_scroll = QScrollArea()
        self.test_select_scroll.setWidgetResizable(True)

        container = QWidget()
        self.scroll_container = QVBoxLayout(container)
        self.test_scroll_lbl = QLabel("Test Selection")
        self.test_scroll_lbl.setFont(QFont("Calibri", 12))
        self.scroll_container.addWidget(self.test_scroll_lbl)

        for i in range(30):
            self.scroll_container.addWidget(QCheckBox(f"Test {i+1}"))
        
        self.scroll_container.addStretch()
        self.test_select_scroll.setWidget(container)
        
        self.test_select_scroll.hide()

        self.run_tests_btn = QPushButton("Run Tests")
        self.run_tests_btn.setObjectName("redButton")
        self.run_tests_btn.hide()
        self.run_tests_btn_row = QHBoxLayout()
        self.run_tests_btn_row.addStretch()
        self.run_tests_btn_row.addWidget(self.run_tests_btn)
        self.run_tests_btn_row.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.enable_check)
        main_layout.addLayout(self.module_id_row)
        main_layout.addWidget(self.test_select_scroll)
        main_layout.addLayout(self.run_tests_btn_row)
        main_layout.addStretch()

        self.subgrid.addLayout(main_layout, 1, 0, 5, 5, Qt.AlignTop)

    def checkbox_changed(self):
        if self.enable_check.isChecked() == True:
            self.module_id_inputbox.setEnabled(True)
            self.module_id_label.show()
            self.module_id_inputbox.show()
            self.test_select_scroll.show()
            self.run_tests_btn.show()
        else:
            self.module_id_inputbox.setEnabled(False)
            self.module_id_label.hide()
            self.module_id_inputbox.hide()
            self.test_select_scroll.hide()
            self.run_tests_btn.hide()

