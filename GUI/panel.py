from PyQt5.QtWidgets import QFrame, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class Panel(QFrame):
    def __init__(self, title):
        super().__init__()

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(5)
        self.setStyleSheet("background-color: #3b3b3b;")
        self.setStyleSheet("""
        QWidget { color: #ffffff; }
        QLabel { color: #ffffff; }
        QLabel:disabled { color: #9aa5b1; }
        QCheckBox { color: #ffffff; }

        QLineEdit, QPlainTextEdit {
            color: #ffffff;
            border: 1px solid #ffffff;
            border-radius: 0px;
            padding: 2px 2px;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            min-height: 20px;
            max-height: 20px;
        }

        QPushButton {
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 4px 8px;
            font-weight: 400;
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
        QPushButton#blueButton:disabled { background-color: #2f4f6f; color: #9aa5b1; }
        """)

        subgrid = QGridLayout(self)
        subgrid.setContentsMargins(8,8,8,8)
        subgrid.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        title_lbl.setStyleSheet("""
                                font-weight: 600;
                                color: #FFFFFF;
                                """)
        #title_lbl.setFont(QFont("Calibri", 12))
        subgrid.addWidget(title_lbl, 0, 0, 1, -1, alignment=Qt.AlignHCenter)

        subgrid.setRowStretch(0, 0)
        subgrid.setRowStretch(1, 1)

        self.subgrid = subgrid
