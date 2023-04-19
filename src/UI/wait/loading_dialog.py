from PyQt5 import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

from src.UI.raw_uis.wait import Ui_Form


class LoadingDialog(QDialog, Ui_Form):
    def __init__(self, parent=None):
        super(LoadingDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Qt.FramelessWindowHint)
        self.setModal(True)
        self.setStyleSheet("background-color: rgb(69, 83, 100);")
        self.move(parent.width() / 2 - self.width() / 2, parent.height() / 2 - self.height() / 2)
        self.setVisible(True)
