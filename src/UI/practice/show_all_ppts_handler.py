from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow

from src.UI.utils.clickable_label import MyQLabel
from src.UI.raw_uis.show_all_ppts import Ui_Dialog


class Show_all_ppts(QMainWindow, Ui_Dialog):

    ppt_changed = QtCore.pyqtSignal(int)

    def __init__(self, png_li):
        super(Show_all_ppts, self).__init__()
        self.setupUi(self)

        self.__png_li = png_li

        self.total = len(png_li)

        self.show_all_ppts()


    def to_ith_ppt(self, i):
        self.ppt_changed.emit(i)
        self.close()


    def show_all_ppts(self):
        """
        创建每行4个可供PNG格式图片展示的QLabel在QScrollArea里
        Qlabel比例固定为16：9
        """
        # QScrollArea的宽度
        scroll_area_width = self.scrollArea.width()
        # QScrollArea的高度
        scroll_area_height = self.scrollArea.height()
        # 每行的Qlabel数量
        label_num = 4
        # 每个Qlabel的宽度
        label_width = (scroll_area_width / label_num)
        # 每个Qlabel的高度
        label_height = label_width * 9 / 16
        # 创建每行4个可供PNG格式图片展示的QLabel， 并且放在QScrollArea里
        for i in range(1, self.total):
            label = MyQLabel(self.scrollArea)
            label.setGeometry(label_width * ((i - 1) % label_num), label_height * ((i - 1) // label_num), label_width, label_height)
            label.setScaledContents(True)
            label.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(self.__png_li[i])))
            label.setObjectName("label")
            # 把 label 放入QScrollArea的内容里，使其可以滚动
            # self.scrollAreaWidgetContents.layout().addWidget(label)
            # 绑定点击事件
            label.connect_customized_slot(lambda i=i: self.to_ith_ppt(i))
            label.show()

        # 设置QScrollArea的高度
        self.scrollArea.setFixedHeight(label_height * (self.total // label_num + 1))
        # 设置QScrollArea的宽度
        self.scrollArea.setFixedWidth(scroll_area_width)
        # 设置QScrollArea的内容
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # 设置QScrollArea的内容的宽度
        self.scrollAreaWidgetContents.setFixedWidth(scroll_area_width * 1.2)
        # 设置QScrollArea的内容的高度
        self.scrollAreaWidgetContents.setFixedHeight(label_height * (self.total // label_num + 1))

        self.show()



