import datetime
import pickle
import re
import time

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QEvent, QPoint, Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel

from src.UI.constants import ERROR_TRNASLATION
from src.UI.editor.exporter import PPTExporter
from src.UI.editor.text_correction_handler import extract_error_positions, parse_result
from src.UI.raw_uis.editor import Ui_Form

import aspose.slides as slides
import aspose.pydrawing as drawing
import io

from src.UI.components.clickable_label import MyQLabel
from src.UI.components.returnable_qthread import MyThread
from src.text_correction_module.text_correction import TextCorrection


class MyEditor(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(MyEditor, self).__init__(parent)
        self.setupUi(self)

        self.__FACECADE = b'11111010110011101100101011011110'

        self.LOAD.clicked.connect(self.on_click)
        self.SAVE.clicked.connect(self.on_click)
        self.ADD_PPT.clicked.connect(self.on_click)
        self.IS_ZD.clicked.connect(self.on_click)
        self.BACK.clicked.connect(self.on_click)
        self.EXPORT.clicked.connect(self.on_click)
        self.TEXT_CORRECTION.clicked.connect(self.on_click)

        self.is_ZD = False  # 默认false

        self.__png_li = []
        self.__text_li = []
        self.now_page = 1

        self.ui_init()


    def ui_init(self):
        """some ui init"""
        self.textEdit.setAcceptRichText(False)

    def is_loaded(self):
        return len(self.__png_li) != 0


    def on_click(self):

        if self.sender() == self.LOAD:
            if self.__load():
                self.__show()
        elif self.sender() == self.BACK:
            self.__back()
        elif self.sender() == self.ADD_PPT:
            self.__add_ppt()
        elif self.sender() == self.IS_ZD:
            self.__judge_ZD()

        # 保存和导出需要判断是否加载了
        elif self.is_loaded():
            if self.sender() == self.SAVE:
                self.__save()
            elif self.sender() == self.EXPORT:
                self.__export()
            elif self.sender() == self.TEXT_CORRECTION:
                self.__text_correction()

    def __text_correction(self):
        """
        使用TextCorrection进行纠正
        :return:
        """
        # 如果当前text没有东西，就不可以纠正
        if self.textEdit.toPlainText() == "":
            return
        # 保存当前页面的文字，因为设置为点击保存上次的
        self.__text_li[self.now_page] = self.textEdit.toPlainText()
        # 不使用线程进行纠正
        # 考虑到在纠正时需要改变当前草稿页面内容
        # 用户行为逻辑会变得复杂，业务逻辑会变得冗余复杂

        # 纠正评测
        text = self.textEdit.toPlainText()
        text_cor = TextCorrection(text)
        self.result = text_cor.get_result()

        corrected_text, result_sub_list = parse_result(text, self.result)

        # set UIs todo 放别的地方，太冗杂了代码
        self.textEdit.setHtml(corrected_text)
        self.textEdit.viewport().installEventFilter(self)
        self.textEdit.setMouseTracking(True)

        self.tooltip_label = QLabel(self)
        self.tooltip_label.setWindowFlags(Qt.ToolTip)
        self.tooltip_label.setStyleSheet("QLabel {background-color: rgba(245, 204, 8, 122); border: 1px solid black; font-color: black}")
        self.tooltip_label.hide()

        self.error_positions = extract_error_positions(corrected_text)

        self.plain_text_error_positions = []
        for start, contents, cor_text, error_type in result_sub_list:
            length = len(contents)
            self.plain_text_error_positions.append((start, length, error_type, cor_text))

    def update_error_positions(self):
        # 获取当前纯文本内容
        current_plain_text = self.textEdit.toPlainText()

        # 创建一个新的纯文本错误位置列表
        updated_plain_text_error_positions = []

        # 遍历原始纯文本错误位置列表
        for pos, length, error_type in self.plain_text_error_positions:
            # 检查错误文本是否仍存在于当前纯文本中
            if current_plain_text[pos:pos + length] == self.result[pos]:
                # 如果错误仍然存在，将其添加到新列表中
                updated_plain_text_error_positions.append((pos, length, error_type))

        # 更新纯文本错误位置列表
        self.plain_text_error_positions = updated_plain_text_error_positions


    def eventFilter(self, source, event):
        if source == self.textEdit and event.type() == QEvent.KeyRelease:
            # 添加内容更改检测 todo 没触发
            QTimer.singleShot(0, self.update_error_positions)
        if event.type() == QEvent.MouseMove and source is self.textEdit.viewport():
            cursor = self.textEdit.cursorForPosition(event.pos())
            cursor_pos = cursor.position()
            for start, length, error_type, correct_contents in self.plain_text_error_positions:
                if start <= cursor_pos < start + length:
                    # 错误类型以及正确内容
                    additional_contents = ""
                    if len(correct_contents) == 0:  # 没有内容不显示
                        additional_contents = f", 应该是{correct_contents}?"
                    self.tooltip_label.setText(f"{ERROR_TRNASLATION[error_type]}{additional_contents}")
                    cursor_rect = self.textEdit.cursorRect(cursor)
                    global_position = self.textEdit.viewport().mapToGlobal(cursor_rect.topLeft())
                    self.tooltip_label.move(global_position - QPoint(0, self.tooltip_label.height()))
                    self.tooltip_label.adjustSize()
                    self.tooltip_label.show()
                    break
            else:
                self.tooltip_label.hide()

        return super().eventFilter(source, event)


    def __export(self):
        exporter = PPTExporter(self.__text_li)
        exporter.export_to_pdf()

    def __back(self):
        from src.UI.index.index_handler import MyIndex
        self.index = MyIndex()
        self.index.show()
        self.hide()


    def __judge_ZD(self):
        self.is_ZD = self.IS_ZD.isChecked()

    def __load(self):
        """
        选择一个pkl加载，加载文字，加载png，并且放入buffer
        """
        pkl_path = QFileDialog.getOpenFileName(self, '选择文件', '', 'Pickle files(*.pkl)')
        pkl_path = str(pkl_path[0])
        if pkl_path == "":
            print("啥也没选")
            return False
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        try:
            self.is_ZD = data["is_zd"]
            length = len(data["data"]) - 1
            self.__png_li.clear()
            self.__png_li.append(self.__FACECADE)
            self.__text_li.clear()
            self.__text_li.append("FACECADE")

            for i in range(1, length + 1):
                self.__png_li.append(data["data"][i]["image"])
                self.__text_li.append(data["data"][i]["text"])

            return True
        except Exception as e:
            print("随便拿个pkl糊不过去的")


    def __save(self):
        """
        保存文字
        读取buffer的png成字节保存
        """
        if len(self.__text_li) == 0 or len(self.__png_li) == 0:
            print("啥都没有不保存")
            return
        # 保存当前页面的文字，因为设置为点击保存上次的
        self.__text_li[self.now_page] = self.textEdit.toPlainText()

        data = {}
        data["time"] = str(datetime.datetime.now())
        data["data"] = []
        data["data"].append({})
        data["is_zd"] = self.is_ZD
        for i in range(1, len(self.__png_li)):
            temp = {"image": self.__png_li[i], "text": self.__text_li[i]}
            data["data"].append(temp)
        # 选择一个path保存, 自定义名字
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        file_path, _ = QFileDialog.getSaveFileName(self, '保存字典', '', 'Pickle Files (*.pkl)', options=options)
        if file_path:
            if not file_path.endswith('.pkl'):
                file_path += '.pkl'

            with open(file_path, 'wb') as f:
                pickle.dump(data, f)

            print(f'saved to: {file_path}')

    def __show(self):
        """将PPT和TEXT展现"""
        self.__load_ppt_from_buffer()
        self.__load_text_from_buffer()


    def __load_ppt_from_buffer(self):
        """
        将buffer的PPT加载入界面中
        :return:
        """
        # 清空

        # 读取png
        num = len(self.__png_li) - 1
        # 1. 通过宽度计算高h
        label_width = self.scrollArea.width()
        label_height = int((label_width / 16) * 9)

        # 2. 总高为num * h, 设置在scrollAreaWidgetContents的minimum size的height
        total_height = num * label_height
        self.scrollAreaWidgetContents.setMinimumHeight(total_height)
        self.scrollAreaWidgetContents.setGeometry(0, 0, label_width, total_height)
        self.layoutWidget.setGeometry(0, 0, label_width, total_height)
        # 3. 创建num个h高度和宽度的label放入verticalLayout_2里面
        for i in range(1, num + 1):
            exec(f"self.PPT_WAITER_{i} = MyQLabel()")  # self.layoutWidget
            exec(f"self.PPT_WAITER_{i}.setObjectName(\"PPT_WAITER_{i}\")")
            exec(f"self.verticalLayout_2.addWidget(self.PPT_WAITER_{i})")
        # 4. 加载ppt进去
        for i in range(1, num + 1):
            # 放入label
            content = self.__png_li[i]
            image = Image.open(io.BytesIO(content))
            q_image = QPixmap.fromImage(ImageQt(image))

            ppt_waiter = getattr(self, f"PPT_WAITER_{i}")
            ppt_waiter.setScaledContents(True)
            ppt_waiter.setPixmap(q_image)
            ppt_waiter.connect_customized_slot(self.__click_ppt)  # 添加了PPT才可以编写


    def __click_ppt(self):
        # 存储当前的内容到当前index
        self.__text_li[self.now_page] = self.textEdit.toPlainText()
        getattr(self, F"PPT_WAITER_{self.now_page}").setStyleSheet("")

        # 切换
        index = int(self.sender().objectName().replace("PPT_WAITER_", ""))
        self.now_page = index

        # 加载预存的文本内容
        self.textEdit.setText(self.__text_li[self.now_page])
        self.sender().setStyleSheet("border: 2px solid; border-color: rgb(69, 83, 100)")

    def __load_text_from_buffer(self):
        """
        text init to index = 1
        """
        self.now_page = 1
        self.textEdit.setText(self.__text_li[self.now_page])


    def __add_ppt(self):
        """
        ppt init
        :return:
        """
        config_path = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.pptx)')
        pptx_path = str(config_path[0])
        if pptx_path == '':
            print("啥也没选")
            return
        else:
            # 清空
            self.__clear_all()

            # 弹出窗口告示请稍后

            from src.UI.wait.loading_dialog import LoadingDialog
            self.wait = LoadingDialog(self)
            self.wait.show()

            t1 = MyThread(save_ppt_to_buffer, pptx_path)
            t1.result_signal.connect(self.__save_ppt_to_buffer)
            t1.start()


    def __save_ppt_to_buffer(self, res):
        self.__png_li = res
        self.__load_ppt_from_buffer()
        # 窗口关闭
        self.wait.close()
        # 初始化text li的内容
        self.__text_li = ["" for i in range(len(self.__png_li))]
        self.__load_text_from_buffer()

    def __clear_all(self):
        # 清理 list
        self.__png_li.clear()
        self.__text_li.clear()
        # 清理 text
        self.textEdit.clear()
        # 清理 label
        try:
            for i in range(1, 100):
                getattr(self, F"PPT_WAITER_{i}").deleteLater()
        except Exception as e:
            print(e)


def save_ppt_to_buffer(ppt_path):
    """
    a thread needed to run this function
    :return:
    """
    ppt_path = ppt_path[0]
    png_li = []
    png_li.append(b'11111010110011101100101011011110')
    if ppt_path is not None:
        with slides.Presentation(ppt_path) as prs:
            for slide in prs.slides:
                stream = io.BytesIO()
                slide.get_thumbnail(2, 2).save(stream, drawing.imaging.ImageFormat.png)
                png_li.append(stream.getvalue())
                stream.close()
        return png_li
    else:
        pass