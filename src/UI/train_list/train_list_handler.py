# 给出一个静态稿件的list,选择
# 然后可以进去练习,加载practice_handler,但是禁用 加载稿件 按钮
import os
import pickle

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow

from src.UI.raw_uis.train_list import Ui_Form
from src.UI.components.clickable_label import MyQLabel


class MyTrainList(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyTrainList, self).__init__(parent)
        self.setupUi(self)

        self.__static_manuscripts_li = []

        self.__load_static_manuscript()

        self.BACK.clicked.connect(self.on_clicked)

        self.init_ui()

    def on_clicked(self):
        """
        处理点击事件
        :return:
        """
        if self.sender() == self.BACK:
            self.__back()

    def __back(self):
        """
        返回index
        :return:
        """
        from src.UI.index.index_handler import MyIndex
        self.index = MyIndex()
        self.index.show()
        self.hide()

    def init_ui(self):
        """
        对静态稿件的数量进行部署len(self.static_manuscripts_li)个MyQLabel
        其中第i个Label展示一个图片, 其png的字节码存储在static_manuscripts_li[i]["data"][1]["image"]里
        MyQlabel的宽度和self.verticalLayout一致
        宽高比为16:9
        self.scrollAreaWidgetContents的minimunSize的高度为len(self.static_manuscripts_li)个MyQLabel的高度之和
        :return:
        """
        total_statics = len(self.__static_manuscripts_li)
        label_width = self.scrollArea.width()
        label_height = int((label_width / 16) * 9)
        for i in range(total_statics):
            # 读取图片的字节码
            data = self.__static_manuscripts_li[i]["data"][1]["image"]
            # 生成QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            # 生成MyQLabel
            my_label = MyQLabel(self)
            my_label.setPixmap(pixmap)
            my_label.setScaledContents(True)
            # 设置MyQLabel的宽度和self.verticalLayout一致
            my_label.setFixedWidth(label_width)
            # 设置MyQLabel的高度为宽度的16/9
            my_label.setFixedHeight(label_height)
            # 将MyQLabel添加到self.verticalLayout中
            self.verticalLayout.addWidget(my_label)
            # 绑定点击事件
            my_label.connect_customized_slot(lambda i=i: self.to_ith_static(i))
        # 设置self.scrollAreaWidgetContents的minimunSize的高度为len(self.static_manuscripts_li)个MyQLabel的高度之和
        total_height = total_statics * label_height
        self.scrollAreaWidgetContents.setGeometry(0, 0, label_width, total_height)
        self.scrollAreaWidgetContents.setMinimumHeight(total_height)
        self.verticalLayoutWidget.setGeometry(0, 0, label_width, total_height)

    def to_ith_static(self, x):
        """
        加载index=x的稿件,打开MyPractice
        :param x:
        :return:
        """
        from src.UI.practice.practice_handler import MyPractice
        self.practice = MyPractice()
        self.practice.load(data_dict=self.__static_manuscripts_li[x])
        self.practice.show()
        self.hide()


    def __load_static_manuscript(self):
        """
        加载"documents/static manuscripts"下的所有pkl静态稿件文件
        :return:
        """
        # 获取documents/static manuscripts下的所有文件名
        path = "../src/documents/static manuscripts"
        file_names = os.listdir(path)
        # 读取所有文件
        for file_name in file_names:
            with open(os.path.join(path, file_name), "rb") as f:
                self.__static_manuscripts_li.append(pickle.load(f))
        return


