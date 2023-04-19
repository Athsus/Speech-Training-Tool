from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QLabel


class TimerLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self.update_time)

        self._hours = 0
        self._minutes = 0
        self._seconds = 0

        self.setText("00:00:00")

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def reset(self):
        self._hours = 0
        self._minutes = 0
        self._seconds = 0
        self.setText("00:00:00")

    def update_time(self):
        self._seconds += 1
        if self._seconds == 60:
            self._seconds = 0
            self._minutes += 1
            if self._minutes == 60:
                self._minutes = 0
                self._hours += 1
        self.setText("{:02d}:{:02d}:{:02d}".format(self._hours, self._minutes, self._seconds))