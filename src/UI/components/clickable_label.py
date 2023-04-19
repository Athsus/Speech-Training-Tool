from PyQt5.QtCore import pyqtSignal
from qtpy import QtWidgets


class MyQLabel(QtWidgets.QLabel):
    button_clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MyQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, QMouseEvent):
        self.button_clicked_signal.emit()

    # 外部槽函数连接
    def connect_customized_slot(self, func):
        self.button_clicked_signal.connect(func)

