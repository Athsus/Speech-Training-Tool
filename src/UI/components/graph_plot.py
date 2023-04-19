import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

dark_style = {
    "figure.facecolor": "#455364",
    "axes.facecolor": "#19232D",
    "axes.edgecolor": "#455364",
    "axes.grid": True,
    "grid.color": "#3C4A57",
    "grid.linestyle": "--",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.labelcolor": "white",
    "xtick.color": "#C7C7C7",
    "ytick.color": "#C7C7C7",
    "xtick.direction": "out",
    "ytick.direction": "out",
    "text.color": "#C7C7C7",
    "font.size": 9,
    "lines.linewidth": 2,
    "lines.markersize": 6,
    "lines.color": "#68B2DE",
    "axes.prop_cycle": plt.cycler(
        color=["#3CB44B", "#4363D8", "#FFD700", "#DC143C", "#FF4500", "#808080", "#FF69B4", "#800000"]),
}

plt.style.use(dark_style)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class MyFigure(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MyFigure, self).__init__(self.fig)

        self.setParent(parent)
