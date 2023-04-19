import random
from PyQt5.QtWidgets import QFileDialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import os
from reportlab.lib import colors
from reportlab.lib.units import cm


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
        indent = "    "
        y_position = letter[1] - margin

        # First line
        c.setFillColor(colors.blue)
        c.drawString(margin, y_position, "void presentation() {")
        y_position -= line_height

        # Content
        for i, text in enumerate(self.manuscript[1:], start=1):
            styled_text = f'ppt[{i}] = "'
            c.setFillColor(colors.black)
            c.drawString(margin + c.stringWidth(indent), y_position, indent + styled_text)

            text_width = c.stringWidth(text)
            max_width = letter[0] - 2 * margin - c.stringWidth(indent + styled_text + '";')

            if text_width <= max_width:
                c.setFillColor(colors.Color(163 / 255, 21 / 255, 21 / 255))
                c.drawString(margin + c.stringWidth(indent + styled_text), y_position, text)
                c.setFillColor(colors.black)
                c.drawString(margin + c.stringWidth(indent + styled_text + text), y_position, '";')
            else:
                words = text.split(" ")
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
