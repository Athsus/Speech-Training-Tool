from PyQt5.QtWidgets import QMainWindow

from src.UI.raw_uis.index import Ui_Form


class MyIndex(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyIndex, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("主页")
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.editor_but.clicked.connect(self.on_click)
        self.practice_but.clicked.connect(self.on_click)
        self.free_but.clicked.connect(self.on_click)
        self.oral_but.clicked.connect(self.on_click)


    def on_click(self):
        if self.sender() == self.editor_but:
            self.__editor_event()
        elif self.sender() == self.practice_but:
            self.__practice_event()
        elif self.sender() == self.free_but:
            self.__free_event()
        elif self.sender() == self.oral_but:
            self.__oral_event()

    def __oral_event(self):
        # to oral
        from src.UI.train_list.train_list_handler import MyTrainList
        self.train_list = MyTrainList()
        self.train_list.show()
        self.hide()

    def __practice_event(self):
        # to practice
        from src.UI.practice.practice_handler import MyPractice
        self.practice = MyPractice()
        self.practice.show()
        self.hide()

    def __editor_event(self):
        # to editor
        from src.UI.editor.editor_handler import MyEditor
        self.editor = MyEditor()
        self.editor.show()
        self.hide()

    def __free_event(self):
        # to freer
        from src.UI.free.free_handler import MyFree
        self.free = MyFree()
        self.free.show()
        self.hide()