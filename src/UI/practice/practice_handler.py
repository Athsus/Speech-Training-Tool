import pickle

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from src.UI.raw_uis.practice import Ui_Form
from src.UI.practice.timer import TimerLabel
from src.evaluate_module.ise import IFlytekISE
from src.recongnition_handler.rtasr import IFlytekRTASR

import re


class MyPractice(QMainWindow, Ui_Form):

    ppt_changed = QtCore.pyqtSignal(int)

    def __init__(self):
        super(MyPractice, self).__init__()
        self.setupUi(self)

        self.halted = False

        # 将self.TIMER 它是label类，更换为TimerLabel
        self.TIMER.deleteLater()
        self.TIMER = TimerLabel(self)
        self.TIMER.setGeometry(10, 50, 91, 21)
        self.TIMER.setObjectName("TIMER")

        self.has_saved_audio = False  # 控制audio的save与否

        self.START.clicked.connect(self.on_click)
        self.PAUSE.clicked.connect(self.on_click)
        self.HALT.clicked.connect(self.on_click)
        self.LOAD.clicked.connect(self.on_click)
        self.LAST.clicked.connect(self.on_click)
        self.NEXT.clicked.connect(self.on_click)
        self.SHOW_ALL_PPTS.clicked.connect(self.on_click)
        self.BACK.clicked.connect(self.on_click)
        self.EVALUATE.clicked.connect(self.on_click)
        self.PLAY.clicked.connect(self.on_click)

        self.rtasr = IFlytekRTASR(self.RECONG)

        self.__png_li = []
        self.__text_li = []
        with open("documents/images/end.png", "rb") as f:
            self.__FACECADE = f.read()
        self.now_page = 1


    def on_click(self):

        if self.sender() == self.LOAD:
            self.__load_manuscript()
        elif self.sender() == self.BACK:
            self.__back()

        if len(self.__text_li) == 0 or len(self.__png_li) == 0:
            print("未加载稿件")
        elif self.sender() == self.PAUSE:
            self.__pause()
        elif self.sender() == self.HALT:
            self.__halt()
        elif self.sender() == self.START:
            self.__start()
        elif self.sender() == self.LAST:
            self.__last()
        elif self.sender() == self.NEXT:
            self.__next()
        elif self.sender() == self.SHOW_ALL_PPTS:
            self.__show_all_ppts()
        elif self.sender() == self.EVALUATE:
            self.__evaluate()

        if self.has_saved_audio and self.sender() == self.PLAY:
            self.__player()


    def __player(self):
        """
        播放录音
        :return:
        """
        from src.UI.player.player import AudioPlayer
        self.player = AudioPlayer()
        self.player.show()

    def __evaluate(self):
        """
        点击评价，展示评价界面
        :return:
        """
        # 先停止录音
        self.__halt()
        # 没有读过就不要评价
        if self.has_saved_audio is False:
            print("没有读过就不要评价了")
            return

        # 处理文本
        text_all = ""
        for i, text in enumerate(self.__text_li):
            if len(text) == 0:  # 这一张PPT就没写内容的话
                continue
            # add dot to the end of each sentence
            if i == 0:
                continue
            if text[-1] != '。':
                text_all += text + "。\n\n"
            else:
                text_all += text + "\n\n"
        # 去除text_all里所有的除了中文的符号, 但是不要去除'\n'
        text_all = re.sub(r'[^\u4e00-\u9fa5\n]', '', text_all)
        ise = IFlytekISE(text_all)
        ise.start()
        ise.emit_res.connect(self.__display_eva)
        # 加载的时候loading dialog跳出，加载完毕后再显示Evaluate,并且关闭loading dialog
        from src.UI.wait.loading_dialog import LoadingDialog
        self.loading = LoadingDialog(self)
        self.loading.show()
        ise.emit_res.connect(self.loading.close)

    def __display_eva(self, res):
        if res == {}:
            print("error, res is {}, retry evaluate!")
            return
        from src.UI.evaluate.evaluate_handler import MyEvaluate
        self.evaluate = MyEvaluate(res["result"], res["text"])
        self.evaluate.show()

    def __back(self):
        self.rtasr.close()
        from src.UI.index.index_handler import MyIndex
        self.index = MyIndex()
        self.index.show()
        self.hide()

    def __to_ith_ppt(self, i):
        """
        跳转到第i张ppt, 从1开始
        主要被show_all_ppts调用
        :param i:
        :return:
        """
        self.now_page = i
        self.__show()

    def __show_all_ppts(self):
        """
        打开Show_all_ppts
        """
        from src.UI.practice.show_all_ppts_handler import Show_all_ppts
        self.show_all_ppts = Show_all_ppts(self.__png_li)
        self.show_all_ppts.show()
        # 如果点击了某一张ppt，就会发射ppt_changed信号，这里接收到信号后，就会调用to_ith_ppt函数
        self.show_all_ppts.ppt_changed.connect(self.__to_ith_ppt)


    def __last(self):
        if self.now_page > 1:
            self.now_page -= 1
            self.__show()


    def __next(self):
        if self.now_page < len(self.__png_li) - 1:
            self.now_page += 1
            self.__show()

    def __show(self):
        """
        思路
        将self.__png_li[self.now_page]中的二进制png格式图片显示在self.PPT上
        将self.__text_li[self.now_page]中的文字显示在self.TEXT上
        将self.__png_li[self.now_page + 1]中的图片显示在self.PPT_2上,如果没有，显示全黑图像
        """
        # 将self.__png_li[self.now_page]中的二进制png格式图片显示在self.PPT上
        self.PPT.setScaledContents(True)
        self.PPT.setPixmap(QPixmap())
        self.PPT.setPixmap(QPixmap.fromImage(QImage.fromData(self.__png_li[self.now_page])))
        # 将self.__text_li[self.now_page]中的文字显示在self.TEXT上
        self.TEXT.setText(self.__text_li[self.now_page])
        # 将self.__png_li[self.now_page + 1]中的图片显示在self.PPT_2上,如果没有，显示全黑图像
        self.PPT_2.setScaledContents(True)
        if self.now_page + 1 < len(self.__png_li):
            self.PPT_2.setPixmap(QPixmap())
            self.PPT_2.setPixmap(QPixmap.fromImage(QImage.fromData(self.__png_li[self.now_page + 1])))
        else:
            self.PPT_2.setPixmap(QPixmap())
            self.PPT_2.setPixmap(QPixmap.fromImage(QImage.fromData(self.__FACECADE)))

    def __load_manuscript(self):
        """choose a manuscript (.pkl)"""
        pkl_path = QFileDialog.getOpenFileName(self, '选择文件', '', 'Pickle files(*.pkl)')
        pkl_path = str(pkl_path[0])
        if pkl_path == "":
            return False
        self.load(pkl_path=pkl_path)

    def load(self, pkl_path=None, data_dict=None):
        """parse pkl to buffer"""
        # 两个参数有且仅能有其一
        if pkl_path is not None:
            with open(pkl_path, "rb") as f:
                data = pickle.load(f)
        elif data_dict is not None:
            data = data_dict
        else:
            raise Exception(f"error parameter with pkl_path is {pkl_path} and data_dict is {data_dict}")
        try:
            self.is_ZD = data["is_zd"]
            length = len(data["data"]) - 1
            self.__png_li.clear()
            self.__png_li.append(self.__FACECADE)
            self.__text_li.clear()
            self.__text_li.append("END")

            for i in range(1, length + 1):
                self.__png_li.append(data["data"][i]["image"])
                self.__text_li.append(data["data"][i]["text"])

            self.__show()
            self.show()

        except Exception as e:
            print(f"pkl parse exception: {e.args}")


    def __start(self):
        if self.rtasr.isRunning():
            print("不可多按开始")
            return
        self.TIMER.start()
        self.TIMER.update_time()
        # 录音
        self.halted = False
        self.rtasr.start()

    def __pause(self):
        self.TIMER.stop()
        # 暂停录音
        if self.rtasr.isRunning():
            self.rtasr.close()

    def __halt(self):
        self.TIMER.stop()
        self.TIMER.reset()

        if self.rtasr.isRunning():
            self.rtasr.close()
        self.halted = True
        self.has_saved_audio = True





