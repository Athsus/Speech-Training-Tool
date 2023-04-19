from PyQt5.QtCore import QThread, pyqtSignal


class MyThread(QThread):
    result_signal = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        # Call the method you want to execute here
        result = self.the_func()

        # Emit the result_signal with the result as an argument
        self.result_signal.emit(result)

    def the_func(self):
        return self.func(self.args)

