import sys
import random
from PyQt5.QtWidgets import QApplication, QFileDialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

song = "simsun"
msyhbd = "msyhbd"
pdfmetrics.registerFont(TTFont(msyhbd, "simsun.ttc"))


class PPTExporter:
    def __init__(self, manuscript):
        self.manuscript = manuscript

    def random_color(self):
        # todo 应用一个配色配置，而不是random
        return Color(random.random(), random.random(), random.random())

    def export_to_pdf(self, save_path=None):
        if save_path is None:
            save_path = QFileDialog.getSaveFileName(None, "Save PDF", os.path.expanduser("~/Desktop"), "PDF Files (*.pdf)")[0]
            if not save_path:
                return
            if not save_path.endswith('.pdf'):
                save_path += '.pdf'

        c = canvas.Canvas(save_path, pagesize=letter)

        # 更改编码
        for i, text in enumerate(self.manuscript[1:], start=1):
            styled_text = f'PPT[{i}] = "{text}";'
            c.setFont(msyhbd, 10)
            c.setFillColor(self.random_color())
            c.drawString(50, 700 - i * 10, styled_text)

        c.save()
        print(f"PDF saved to {save_path}")


# Example usage
# manuscript = ["facecade", "大家好", "这是一个测试ppt"]
# exporter = PPTExporter(manuscript)
# exporter.export_to_pdf()
