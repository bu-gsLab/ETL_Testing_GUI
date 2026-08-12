import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QGridLayout, QVBoxLayout, QTabWidget, QStackedLayout
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from pathlib import Path

from .coldbox_panel import ColdboxPanel
from .daq_panel import DAQPanel

MAIN_DIR = Path(__file__).parent.parent
gui_dir = MAIN_DIR / "GUI"
sys.path.append(str(gui_dir))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ETL Testing GUI")
        #self.setFixedSize(QSize(2500, 2000))
        self.setStyleSheet("background-color: #3b3b3b;")
        self.setWindowIcon(QIcon(str(gui_dir / "icon.png")))

        # ----- Main Layout -----
        self.main_layout = QGridLayout()

        # ----- Build Tabs -----
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.DAQ_tab = QWidget()
        self.coldbox_tab = QWidget()

        self.DAQ_tab_layout = QVBoxLayout(self.DAQ_tab)
        self.coldbox_tab_layout = QVBoxLayout(self.coldbox_tab)

        self.DAQ_frame = DAQPanel()
        self.coldbox_frame = ColdboxPanel()

        self.DAQ_tab_layout.addWidget(self.DAQ_frame)
        self.coldbox_tab_layout.addWidget(self.coldbox_frame)

        self.tabs.addTab(self.DAQ_tab, "DAQ")
        self.tabs.addTab(self.coldbox_tab, "Coldbox")
        self.tabs.setStyleSheet("QTabBar::tab { color: white; }")

        self._shutting_down = False

    def closeEvent(self, event):
        """Stop acquisition and disconnect hardware before exiting."""
        if self._shutting_down:
            event.accept()
            return

        self._shutting_down = True
        try:
            for component in (self.DAQ_frame, self.coldbox_frame):
                try:
                    component.shutdown()
                except Exception as error:
                    # Continue so one cleanup error cannot strand the other
                    # background threads or processes.
                    print(f"Error while shutting down the GUI: {error}")
        finally:
            event.accept()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    app.setWindowIcon(QIcon(str(gui_dir / "icon.png")))
    window = MainWindow()
    window.resize(1200, window.sizeHint().height())
    window.show()
    sys.exit(app.exec_())
