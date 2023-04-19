from PyQt5 import QtWidgets, QtCore, QtGui


class CustomTitleBar(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setStyleSheet("""
            CustomTitleBar {{
                background-color: #2C3E50;
                height: 30px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
            QLabel {{
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding-left: 5px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #1ABC9C;
            }}
            QPushButton:pressed {{
                color: #16A085;
            }}
        """)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QtWidgets.QLabel("Custom Title Bar")
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.minimize_button = QtWidgets.QPushButton("-")
        self.minimize_button.setMaximumSize(QtCore.QSize(20, 20))
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.layout.addWidget(self.minimize_button)
        self.close_button = QtWidgets.QPushButton("x")
        self.close_button.setMaximumSize(QtCore.QSize(20, 20))
        self.close_button.clicked.connect(self.parent.close)
        self.layout.addWidget(self.close_button)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.title_bar = CustomTitleBar(self)
        self.setFixedSize(400, 300)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.title_bar)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.slider)
        self.time_label = QtWidgets.QLabel("00:00 / 00:00")
        self.layout.addWidget(self.time_label)
        self.play_button = QtWidgets.QPushButton("Play")
        self.layout.addWidget(self.play_button)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()