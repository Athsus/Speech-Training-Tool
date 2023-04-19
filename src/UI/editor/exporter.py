import random
from PyQt5.QtWidgets import QFileDialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import os
from reportlab.lib import colors
from reportlab.lib.units import cm

pdfmetrics.registerFont(TTFont("SimSun", "simsun.ttc"))


class PPTExporter:
    def __init__(self, manuscript):
        self.manuscript = manuscript

    def random_color(self):
        """
        deprecated
        the color should be set instead of randomizing
        """
        return Color(random.random(), random.random(), random.random())

    def export_to_pdf(self, save_path=None):
        """
        导出稿件，默认为仿 visualstudio 的 style
        
        所有字体均为新宋体，页边距为1.27厘米，行间距为1.0。
        内容方面，第一行是 "void presentation() {"，最后一行为 "}"。
        在这其中，"void" 的颜色为蓝色(RGB：0, 0, 255)，而其余部分为黑色。
        中间的内容每行都缩进一个制表符(4个空格)，每一个PPT的输出内容为 "ppt[i] = '第i章ppt的稿件，是这些内容。';"。
        若遇到句号，则换行。在换行后，下一个 "ppt[i]" 将回到仅缩进一个制表符的位置。
        同时，稿件内容的文本颜色为深红色(RGB：163, 21, 21)，而其他部分保持为黑色。

        """
        if save_path is None:
            save_path = QFileDialog.getSaveFileName(None, "Save PDF", os.path.expanduser("~/Desktop"), "PDF Files (*.pdf)")[0]
            if not save_path:
                return
            if not save_path.endswith('.pdf'):
                save_path += '.pdf'

        c = canvas.Canvas(save_path, pagesize=letter)
        c.setFont("SimSun", 10)
        margin = 1.27 * cm
        line_height = 1.0 * cm
        indent = " "
        y_position = letter[1] - margin

        # First line
        c.setFillColor(colors.blue)
        c.drawString(margin, y_position, "void presentation() {")
        y_position -= line_height

        # Content
        first_line = True
        for i, text in enumerate(self.manuscript[1:], start=1):
            styled_text = f'ppt[{i}] = "'
            c.setFillColor(colors.black)
            c.drawString(margin + c.stringWidth(indent), y_position, indent + styled_text)

            if first_line:
                text = text.replace("。", "。\n", 1)
                first_line = False
            else:
                text = text.replace("。", "。\n")

            lines = text.split("\n")

            for line in lines:
                text_width = c.stringWidth(line)
                max_width = letter[0] - 2 * margin - c.stringWidth(indent + styled_text + '";')

                if text_width <= max_width:
                    c.setFillColor(colors.Color(163 / 255, 21 / 255, 21 / 255))
                    c.drawString(margin + c.stringWidth(indent + styled_text), y_position, line)
                    c.setFillColor(colors.black)
                    c.drawString(margin + c.stringWidth(indent + styled_text + line), y_position, '";')
                else:
                    words = line.split(" ")
                    current_line = ""
                    for word in words:
                        if c.stringWidth(current_line + " " + word) < max_width:
                            current_line += " " + word
                        else:
                            c.setFillColor(colors.Color(163 / 255, 21 / 255, 21 / 255))
                            c.drawString(margin + c.stringWidth(indent + styled_text), y_position, current_line)
                            y_position -= line_height
                            current_line = indent + word

                    c.setFillColor(colors.Color(163 / 255, 21 / 255, 21 / 255))
                    c.drawString(margin + c.stringWidth(indent + styled_text), y_position, current_line)
                    c.setFillColor(colors.black)
                    c.drawString(margin + c.stringWidth(indent + styled_text + current_line), y_position, '";')

                y_position -= line_height

        # Last line
        c.setFillColor(colors.black)
        c.drawString(margin, y_position, "}")

        c.save()
        print(f"PDF saved to {save_path}")


# Example usage
# manuscript = ["facecade", "大家好", "这是一个测试ppt"]
# exporter = PPTExporter(manuscript)
# exporter.export_to_pdf()
