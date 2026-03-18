from PyQt5 import QtGui, QtCore, QtWidgets

class CheckableComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                color: #ffffff;
                border: 1px solid #ffffff;
                border-radius: 6px;
                padding: 4px 30px;
                background-color: #3b3b3b;
            }
            QComboBox:disabled {
                color: #9aa5b1;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                color: #ffffff;
                background-color: #3b3b3b;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
                border: 1px solid #ffffff;
            }
        """)

    # once there is a checkState set, it is rendered
    # here we assume default Unchecked
    def addItem(self, item):
        super(CheckableComboBox, self).addItem(item)
        item = self.model().item(self.count()-1,0)
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)

    def itemChecked(self, index):
        item = self.model().item(index,0)
        return item.checkState() == QtCore.Qt.Checked

    def getCheckedItems(self):
        checked_items = []
        for i in range(self.count()):
            item = self.model().item(i, 0)
            if self.itemChecked(i):
                checked_items.append(item.text())
        return checked_items