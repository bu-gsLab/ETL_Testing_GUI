from PyQt5 import QtGui, QtCore, QtWidgets

class CheckableComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.view().setTextElideMode(QtCore.Qt.ElideNone)
        self.model().itemChanged.connect(self._update_selection_text)
        self.setStyleSheet("""
            QComboBox {
                color: #ffffff;
                border: 1px solid #ffffff;
                border-radius: 4px;
                padding: 4px 4px;
                background-color: #3b3b3b;
                min-height: 20px;
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

    def _update_selection_text(self, _item=None):
        if self.count() == 0:
            return

        checked_count = sum(
            self.itemChecked(i)
            for i in range(1, self.count())
        )
        display_text = (
            f"{checked_count} tests selected"
            if checked_count
            else "Select tests..."
        )

        placeholder = self.model().item(0, 0)
        if placeholder.text() != display_text:
            blocker = QtCore.QSignalBlocker(self.model())
            placeholder.setText(display_text)
            del blocker

        self.setCurrentIndex(0)
        self.update()
