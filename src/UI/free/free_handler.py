from PyQt5.QtWidgets import QMainWindow

from src.UI.raw_uis.free import Ui_Free

from src.evaluate_module.ise import IFlytekISE
from src.recongnition_module.rtasr import IFlytekRTASR


# todo: 录音结束会崩溃?

class MyFree(QMainWindow, Ui_Free):

    def __init__(self, parent=None):
        super(MyFree, self).__init__(parent)
        self.setupUi(self)

        self.textBrowser.setReadOnly(True)
        self.rtasr = IFlytekRTASR(self.textBrowser)
        self.rtasr.emit_res.connect(self.__display_res)
        self.START.clicked.connect(self.on_click)
        self.PAUSE.clicked.connect(self.on_click)
        self.HALT.clicked.connect(self.on_click)
        self.BACK.clicked.connect(self.on_click)
        self.JUDGE.clicked.connect(self.on_click)
        self.PLAY.clicked.connect(self.on_click)

        self.halted = False

        self.has_saved_audio = False

    def __display_res(self, text: str):
        if self.halted:
            return
        self.textBrowser.setText(text)

    def on_click(self):
        if self.sender() == self.START:
            self.__start_event()
        elif self.sender() == self.PAUSE:
            self.__pause_event()
        elif self.sender() == self.HALT:
            self.__halt_event()
        elif self.sender() == self.BACK:
            self.__back_event()
        # 如果没有识别,那么就不要进行下面的操作
        if len(self.textBrowser.toPlainText()) == 0:
            print("并没有录音")
        elif self.sender() == self.JUDGE:
            self.__judge_event()
        # 没有音频,就不要播放
        elif self.sender() == self.PLAY and self.has_saved_audio:
            self.__play_event()

    def __play_event(self):
        from src.UI.player.player import AudioPlayer
        self.player = AudioPlayer()
        self.player.show()

    def __judge_event(self):
        self.__halt_event()
        text = self.textBrowser.toPlainText()
        if len(text) == 0:
            print("无文本")
            return
        ise = IFlytekISE(text)
        ise.start()
        # 接收emit的objects，然后display Eva
        ise.emit_res.connect(self.__display_eva)
        # 加载的时候loading dialog跳出，加载完毕后再显示Evaluate,并且关闭loading dialog
        from src.UI.wait.loading_dialog import LoadingDialog
        self.loading = LoadingDialog(self)
        self.loading.show()
        ise.emit_res.connect(self.loading.close)

    def __display_eva(self, res):
        if res == {}:
            print("error in __display_eva")
            return
        from src.UI.evaluate.evaluate_handler import MyEvaluate
        self.evaluate = MyEvaluate(res["result"], res["text"])
        self.evaluate.show()

    def __back_event(self):
        self.rtasr.close()

        self.__halt_event()
        # to main
        from src.UI.index.index_handler import MyIndex
        self.index = MyIndex()
        self.index.show()
        self.hide()

    def __start_event(self):
        """
        开始录音识别
        :return:
        """
        if self.rtasr.isRunning():
            print("不可多按")
            return

        if self.halted:
            self.textBrowser.clear()

        self.halted = False
        self.rtasr.start()

    def __pause_event(self):
        """
        暂停录音识别，保留识别记录
        :return:
        """
        if self.rtasr.isRunning():
            self.rtasr.close()

    def __halt_event(self):
        """
        识别记录，并且下一次重新识别
        :return:
        """
        if self.rtasr.isRunning():
            self.rtasr.close()
        self.halted = True

        self.has_saved_audio = True
