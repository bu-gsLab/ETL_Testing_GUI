import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QVBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from pathlib import Path

from panel import Panel
from rb_panel import RBPanel

class DAQPanel(Panel):
    def __init__(self, title="Data Acquisition and Testing"):
        super().__init__(title)
    
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setFrameShape(QFrame.Shape.NoFrame)

        # ----- Build panels -----

        # ----- Coldbox column: Arduino / Chiller / HV / LV -----
        self.rb_layout = QVBoxLayout()
        self.rb1 = RBPanel(1)
        self.rb2 = RBPanel(2)
        self.rb_layout.addWidget(self.rb1)
        self.rb_layout.addWidget(self.rb2)

        mainlayout = QVBoxLayout()
        mainlayout.addLayout(self.rb_layout)



        self.subgrid.addLayout(mainlayout, 1, 0, 5, 5, Qt.AlignTop)
