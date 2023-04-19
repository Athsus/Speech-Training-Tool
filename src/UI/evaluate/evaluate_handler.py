import numpy as np
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtWidgets import QMainWindow, QGridLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.UI.constants import PUNCTUATION_REGEX_STR, PUNCTUATION_DICT
from src.UI.raw_uis.evaluate import Ui_Form
import re

from src.UI.components.graph_ploter import MyFigure


class MyEvaluate(QMainWindow, Ui_Form):

    def __init__(self, res, text):
        super(MyEvaluate, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("演讲语音评估")

        self.text = text.replace("\ufeff", "").replace("\n", "")
        self.raw_res = res

        # 处理结果
        # 评分数据
        self.average, self.duration_list, self.scores, self.dp_message, self.word_list, self.sentence_score = self.analyze_speech_data(
            self.raw_res, self.text)

        # 画结果波形图
        self.__draw()

        score_res = self.parse_scores(self.scores)

        result = f"平均语速: {round(self.average, 2)} 字/秒\n" + \
                 f"评分: \n{score_res}\n"

        self.__display_result()

        self.RESULT.setText(result)

        self.__ui_optimize()  # 请放在最后，保证所有的控件都已经初始化

    def __ui_optimize(self):
        """
        请放在最后，保证所有的控件都已经初始化
        :return:
        """
        # self.RESULT与self.label在同一水平线上，在self.TEXT右边界向右偏移10个单位
        self.RESULT.move(self.TEXT.x() + self.TEXT.width() + 10, self.RESULT.y())
        # self.WAVE在self.RESULT的下方，与self.RESULT宽度相同
        self.WAVE.setFixedWidth(self.RESULT.width())
        self.WAVE.move(self.RESULT.x(), self.RESULT.y() + self.RESULT.height() + 10)
        # self.WAVE的底部与self.TEXT的底部对齐
        self.WAVE.setFixedHeight(self.TEXT.y() + self.TEXT.height() - self.WAVE.y())


    def __draw(self):
        """
        hidden function to draw the result graph
        结果波形图
        :return:
        """
        self.PLOT = MyFigure()
        self.gridLayout_graph = QGridLayout(self.WAVE)
        self.gridLayout_graph.addWidget(self.PLOT, 0, 1)
        self.plot_speech_rate(self.duration_list)
        # 对整个PLOT的布局进行优化，要贴self.TEXT的正下方，并且宽度相同
        self.gridLayout_graph.setContentsMargins(0, 0, 0, 0)

    def parse_scores(self, score_dict):
        """
        对scores_dict的内容进行中文解析
        每个键值对的值都是一个字符串+'\n'
        :param score_dict:
        :return:
        """
        for key, value in score_dict.items():
            # if key == "accuracy_score":
            #     score_dict[key] = f"准确度: {value}"
            # elif key == "emotion_score":
            #     score_dict[key] = f"情感: {value}"
            if key == "fluency_score":
                score_dict[key] = f"流畅度: {value}"
            elif key == "integrity_score":
                score_dict[key] = f"完整度: {value}"
            elif key == "tone_score":
                score_dict[key] = f"语调: {value}"
            elif key == "total_score":
                score_dict[key] = f"总分: {value}"
        # 转成字符串
        score = "\n".join(score_dict.values())
        return score

    def analyze_speech_data(self, ise_json, target_text):
        """
        解析语音评测数据
        :param ise_json:
        :param target_text:
        :return:
        """
        word_list = target_text.replace("\ufeff", "").replace(",", "").replace(".", "")
        word_count = len(word_list)
        duration = int(ise_json['xml_result']['read_chapter']['rec_paper']['read_chapter']['@end_pos']) * 0.01
        words = []

        sentence = ise_json['xml_result']['read_chapter']['rec_paper']['read_chapter']['sentence']
        if isinstance(sentence, list):
            for temp in sentence:
                if isinstance(temp["word"], list):
                    for word in temp["word"]:
                        words.append(word)
                else:
                    words.append(temp["word"])
        elif isinstance(sentence, dict):  # 只有一个句子
            words = sentence["word"]

        # 计算平均语速
        avg_speech_rate = duration / word_count

        # 计算语速
        word_durations = [int(word["@time_len"]) * 0.01 for word in words]
        scores_temp = ise_json['xml_result']['read_chapter']['rec_paper']['read_chapter']
        scores = {
            'fluency_score': scores_temp["@fluency_score"],
            'integrity_score': scores_temp["@integrity_score"],
            'tone_score': scores_temp["@tone_score"],
            'total_score': scores_temp["@total_score"]
        }

        # 获取每个sencence的total_score
        sentence_score = []
        sentence = scores_temp["sentence"]
        if isinstance(sentence, list):
            for temp in sentence:
                sentence_score.append(temp["@total_score"])
        elif isinstance(sentence, dict):  # 只有一个句子
            sentence_score.append(sentence["@total_score"])

        # 获取每个字的效果，0正常；16漏读；32增读；64回读；128替换；
        dp_message = []
        for dp in words:
            if isinstance(dp['syll'], list):
                dp_message.append(dp['syll'][-1]['@dp_message'])
            else:
                dp_message.append(dp['syll']['@dp_message'])

        return avg_speech_rate, word_durations, scores, dp_message, word_list, sentence_score

    def __display_result(self):
        """
        将结果通过rgb的方式展现在self.TEXT上，要求：
        所有内容展现在self.TEXT上
        dp_message = 0: 正常，标注为绿色(rgb = 6, 220, 124)
        dp_message = 16: 漏读，标注为下划线(__ omit), 并且单字标红(rgb = 242, 65, 55)

        对于分很低的句子<=33，标注为红色(rgb = 242, 65, 55)
        分不太低的句子>33, <=66，标注为黄色(rgb = 245, 204, 8)
        剩余的标注为绿色(rgb = 6, 220, 124)

        内容来自self.text
        句子分数来自self.sentence_score
        dp_message来自self.dp_message
        """
        dp_message = self.dp_message

        colors = {
            "red": (242, 65, 55),
            "yellow": (245, 204, 8),
            "green": (6, 220, 124)
        }

        formatted_text = ""
        sentences = re.split(PUNCTUATION_REGEX_STR, self.text)
        sentence_lengths = []
        for sentence in sentences:
            if len(sentence) == 0:
                continue
            else:
                sentence_lengths.append(len(sentence))

        # 长度为len(self.text) 对应每个字在句子中的颜色
        sentence_color_li = []
        sentence_score = self.sentence_score

        for i, score in enumerate(sentence_score):
            sentence_length = sentence_lengths[i]
            # 拿overall分数，然后对对应的整个句子的每一个字进行上色，标注一个list，在构建html的时候特判
            # 优先级: 变红> 变黄> 变绿，下划线不影响
            score = float(score)
            if score <= 33:
                color = colors["red"]
            elif score <= 66:
                color = colors["yellow"]
            else:
                color = colors["green"]
            # 将当前颜色放入list中
            sentence_color_li += [color for _ in range(sentence_length)]

        i = 0
        for char in self.text:
            under_line_css = ""
            # 标点符号特判
            if char in PUNCTUATION_DICT:
                formatted_text += f"<span>{char}</span>"
                continue
            if dp_message[i] == "0":  # dp正常则按照整句的颜色变化
                color = sentence_color_li[i]
            elif dp_message[i] == "16":  # 漏读强制红下划线
                color = colors["red"]
                under_line_css = "text-decoration: underline;"
            else:
                color = colors["yellow"]  # 其他问题黄掉
            formatted_text += f"<span style='color: rgb{color}; {under_line_css}'>{char}</span>"
            i += 1
        self.TEXT.setHtml(formatted_text)
        return

    def plot_speech_rate(self, speech_rates):
        speech_rates = np.array(speech_rates)
        # 计算峰值和谷值
        peak_indices = np.argpartition(speech_rates, -1)[-1:]
        valley_indices = np.argpartition(speech_rates, 1)[:1]

        # 通过MyFigure在self.PLOT上绘制图像
        self.PLOT.axes.plot(speech_rates)
        self.PLOT.axes.plot(peak_indices, speech_rates[peak_indices], 'ro')
        self.PLOT.axes.plot(valley_indices, speech_rates[valley_indices], 'ro')
        self.PLOT.axes.set_xlabel('时间/秒')
        self.PLOT.axes.set_ylabel('语速/字/秒')
        self.PLOT.axes.set_title('语速波形图')
        # 图标
        self.PLOT.axes.legend(['语速', '峰值', '谷值'])
        # 修正x轴的刻度
        xticks = np.arange(0, len(speech_rates), 5)
        self.PLOT.axes.set_xticks(xticks)
        self.PLOT.axes.tick_params(axis='x', which='minor', bottom=False)
        self.PLOT.axes.grid()
        # 修正y轴的刻度
        yticks = np.arange(0, max(speech_rates) + 0.4, 0.4)
        self.PLOT.axes.set_yticks(yticks)
        self.PLOT.axes.tick_params(axis='y', which='minor', left=False)
        self.PLOT.draw()
