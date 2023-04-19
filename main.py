import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.UI.index.index_handler import MyIndex
import qdarkstyle as qdarkstyle

# todo: bugs
# 容易崩溃：
# QObject::connect: Cannot queue arguments of type 'QTextCursor'
# (Make sure 'QTextCursor' is registered using qRegisterMetaType().)??


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    myWin = MyIndex()
    myWin.show()
    sys.exit(app.exec_())