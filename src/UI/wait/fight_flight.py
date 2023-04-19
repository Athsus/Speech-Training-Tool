import math
import random

from PyQt5.QtCore import QRectF, Qt, QTimer, QThread
from PyQt5.QtGui import QPainter, QColor, QKeyEvent
from PyQt5.QtWidgets import QMainWindow, QGraphicsItem, QGraphicsScene, QGraphicsView, QLabel

from src.UI.raw_uis.wait import Ui_Form

score = 0


class Wait_control(QGraphicsView):
    def __init__(self):
        super(Wait_control, self).__init__()
        # self.setupUi(self)

        self.setFixedSize(800, 600)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(69, 83, 100))

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 800, 600)
        self.setScene(self.scene)

        self.player_plane = PlayerPlane()
        self.scene.addItem(self.player_plane)
        self.player_plane.setPos(400, 500)

        self.enemy_timer = QTimer()
        self.enemy_timer.timeout.connect(self.spawn_enemy)
        self.enemy_timer.start(1000)

        self.score_label = QLabel("Score: 0", self)
        self.score_label.setGeometry(0, 500, 100, 30)

        self.enemy_count = 0

        self.instructions_label = QLabel("Instructions:\nW - Up\nA - Left\nS - Down\nD - Right\nJ - Shoot", self)
        self.instructions_label.setGeometry(0, 0, 200, 200)

    def update_score(self, points):
        global score
        score += points
        self.score_label.setText(f"Score: {score}")

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_W:
            self.player_plane.move(0, -20)
        elif event.key() == Qt.Key_A:
            self.player_plane.move(-20, 0)
        elif event.key() == Qt.Key_S:
            self.player_plane.move(0, 20)
        elif event.key() == Qt.Key_D:
            self.player_plane.move(20, 0)
        elif event.key() == Qt.Key_J:
            bullet = Bullet()
            bullet.setParentItem(self.player_plane)  # 似乎不行
            bullet.setPos(self.player_plane.x() + self.player_plane.boundingRect().width() / 2, self.player_plane.y())
            self.scene.addItem(bullet)

    def spawn_enemy(self):
        if self.enemy_count >= 10:
            self.scene.advance()
        enemy = EnemyPlane(self.player_plane)
        spawn_edge = random.choice(["top", "left", "right"])
        if spawn_edge == "top":
            x = random.randint(0, 800)
            y = 0
        elif spawn_edge == "left":
            x = 0
            y = random.randint(0, 240)
        elif spawn_edge == "right":
            x = 800
            y = random.randint(0, 240)
        enemy.setPos(x, y)
        self.scene.addItem(enemy)
        self.enemy_count += 1
        self.scene.advance()


class PlayerPlane(QGraphicsItem):
    def __init__(self, parent=None):
        super(PlayerPlane, self).__init__(parent)
        self.plane_styles = ["演", "讲", "训", "练"]

    def boundingRect(self):
        return QRectF(0, 0, 20, 20)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setBrush(QColor(255, 255, 255))
        painter.drawText(0, 20, random.choice(self.plane_styles))

    def move(self, dx, dy):
        x = self.x() + dx
        y = self.y() + dy

        if 0 <= x <= 780 and 0 <= y <= 580:
            self.setPos(x, y)
            self.update()


class EnemyPlane(QGraphicsItem):
    def __init__(self, player_plane, parent=None):
        super(EnemyPlane, self).__init__(parent)
        self.player_plane = player_plane
        self.speed = 10

    def boundingRect(self):
        return QRectF(0, 0, 20, 20)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setBrush(QColor(255, 255, 255))
        # painter.drawRect(0, 0, 20, 20)
        painter.drawText(0, 20, "✈️")

    def advance(self, phase):
        if phase:
            dx = self.player_plane.x() - self.x()
            dy = self.player_plane.y() - self.y()
            angle = math.atan2(dy, dx)
            vx = math.cos(angle) * self.speed
            vy = math.sin(angle) * self.speed
            self.setPos(self.x() + vx, self.y() + vy)

            if self.x() < 0 or self.x() > 800 or self.y() < 0 or self.y() > 600:
                self.scene().removeItem(self)
                self.update()


class Bullet(QGraphicsItem):
    def __init__(self, parent=None):
        super(Bullet, self).__init__(parent)

    def boundingRect(self):
        return QRectF(0, 0, 5, 10)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setBrush(Qt.white)
        painter.drawRect(0, 0, 5, 10)
        # painter.drawText(0, 20, "弹")

    def advance(self, phase):
        global score
        if phase:
            self.setPos(self.x(), self.y() - 20)

            if self.y() < 0:
                self.scene().removeItem(self)

            for item in self.collidingItems():
                if isinstance(item, EnemyPlane):
                    self.scene().removeItem(item)
                    self.scene().removeItem(self)
                    score += 1
                    break
# 飞机TODO：
# 1. 撞到子弹有概率崩溃
# 2. 自机撞到敌机不会自爆
# 3. 不计分


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = Wait_control()
    window.show()
    sys.exit(app.exec_())
