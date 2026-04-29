from PyQt5.QtWidgets import QFrame, QLabel, QGridLayout, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

class Panel(QFrame):
    def __init__(self, title):
        super().__init__()

        fm = QFontMetrics(QApplication.font())
        em = fm.height()
        self.em = em

        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(round(em * 0.3))
        self.setStyleSheet(f"""
        QWidget {{ color: #ffffff; }}
        QLabel {{ color: #ffffff; }}
        QLabel:disabled {{ color: #9aa5b1 }}
        QCheckBox {{ color: #ffffff; }}
        QLineEdit, QPlainTextEdit {{
            color: #ffffff;
            border: {max(1, round(em * 0.07))}px solid #ffffff;
            border-radius: 0px;
            padding: {round(em * 0.12)}px {round(em * 0.12)}px;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
            min-height: {round(em * 1.2)}px;
            max-height: {round(em * 1.2)}px;
        }}
        QLineEdit:disabled {{ border: {max(1, round(em * 0.07))}px solid #9aa5b1 }}
        QPushButton {{
            color: #ffffff;
            border: none;
            border-radius: {round(em * 0.6)}px;
            padding: {round(em * 0.25)}px {round(em * 0.5)}px;
            font-weight: 400;
        }}
        QPushButton:disabled {{ color: #9aa5b1; }}

        QPushButton#greenButton {{ background-color: #16a34a; color: #ffffff; }}
        QPushButton#greenButton:hover {{ background-color: #22c55e; }}
        QPushButton#greenButton:pressed {{ background-color: #15803d; }}
        QPushButton#greenButton:disabled {{ background-color: #14532d; color: #9aa5b1; }}

        QPushButton#neutralButton {{ background-color: #4b5563; color: #ffffff; }}
        QPushButton#neutralButton:hover {{ background-color: #6b7280; }}
        QPushButton#neutralButton:pressed {{ background-color: #374151; }}
        QPushButton#neutralButton:disabled {{ background-color: #1f2937; color: #9aa5b1; }}

        QPushButton#redButton {{ background-color: #e53935; color: #ffffff; }}
        QPushButton#redButton:hover {{ background-color: #ef5350; }}
        QPushButton#redButton:pressed {{ background-color: #c62828; }}
        QPushButton#redButton:disabled {{ background-color: #7f1d1d; color: #9aa5b1; }}

        QPushButton#blueButton {{ background-color: #007bff; color: #ffffff; }}
        QPushButton#blueButton:hover {{ background-color: #339cff; }}
        QPushButton#blueButton:pressed {{ background-color: #0056b3; }}
        QPushButton#blueButton:disabled {{ background-color: #9aa5b1; }}
        """)

        margin = round(em * 0.5)
        spacing = round(em * 0.35)

        subgrid = QGridLayout(self)
        subgrid.setContentsMargins(margin, margin, margin, margin)
        subgrid.setSpacing(spacing)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        title_lbl.setStyleSheet("""
            font-weight: 600;
            color: #ffffff;
        """)
        subgrid.addWidget(title_lbl, 0, 0, 1, -1, alignment=Qt.AlignHCenter)
        subgrid.setRowStretch(0, 0)
        subgrid.setRowStretch(1, 1)
        self.subgrid = subgrid