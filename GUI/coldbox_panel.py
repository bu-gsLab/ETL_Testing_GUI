import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from pathlib import Path

from arduino_panel import ArduinoPanel
from chiller_panel import ChillerPanel
from hv_panel import HVPanel
from lv_panel import LVPanel
from panel import Panel

class ColdboxPanel(Panel):
    def __init__(self, title="Coldbox Monitoring & Control"):
        super().__init__(title)
    
        self.setFrameShadow(QFrame.Sunken)

        # ----- Build panels -----
        self.ard = ArduinoPanel()
        self.chill = ChillerPanel()
        self.hv = HVPanel()
        self.lv = LVPanel()    

        # ----- Coldbox column: Arduino / Chiller / HV / LV -----
        self.coldbox_layout = QVBoxLayout()
        self.coldbox_layout.addWidget(self.ard)
        self.coldbox_layout.addWidget(self.chill)
        self.coldbox_layout.addWidget(self.hv)
        self.coldbox_layout.addWidget(self.lv)

        self.subgrid.addLayout(self.coldbox_layout, 1, 0, 5, 5, Qt.AlignTop)
