import sys
import pyaudio
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel

from src.recongnition_handler.rtasr import CHANNELS, RATE, CHUNK


class AudioThread(QThread):
    update_slider = pyqtSignal(int)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        self.running = False
        self.paused = False

    def run(self):
        self.running = True

        # 打开 PCM 文件
        with open(self.audio_file, 'rb') as f:
            data = f.read(CHUNK)

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, output=True)

            while data and self.running:
                if not self.paused:
                    stream.write(data)
                    data = f.read(CHUNK)
                    self.update_slider.emit(CHUNK)
                else:
                    self.msleep(100)  # 暂停时线程休眠

            stream.stop_stream()
            stream.close()
            p.terminate()

    def pause(self):
        self.paused = not self.paused

    def stop(self):
        self.running = False


# todo AUDIOPLAYER bugs
# 1. 播放时，无法拖动进度条
# 2. 暂停时，拖动进度条对音频播放位置无效

class AudioPlayer(QWidget):
    def __init__(self, audio_file="documents/audios/ise_audio.pcm"):
        super().__init__()

        self.duration_seconds, self.total_bytes = self.get_duration(audio_file)
        self.max_minutes = self.duration_seconds // 60
        self.max_seconds = self.duration_seconds % 60

        self.audio_thread = AudioThread(audio_file)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('音频播放器')

        # 设置长宽
        self.resize(700, 130)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        self.play_button = QPushButton('播放', self)
        self.play_button.clicked.connect(self.play_pause)
        hbox.addWidget(self.play_button)

        self.stop_button = QPushButton('停止', self)
        self.stop_button.clicked.connect(self.stop)
        hbox.addWidget(self.stop_button)

        vbox.addLayout(hbox)

        self.slider = QSlider(Qt.Horizontal, self)
        vbox.addWidget(self.slider)
        self.slider.setRange(0, self.total_bytes)

        self.label = QLabel('00:00', self)
        vbox.addWidget(self.label)

        self.setLayout(vbox)

        self.audio_thread.update_slider.connect(self.update_slider)

    def get_duration(self, audio_file):
        with open(audio_file, 'rb') as f:
            data = f.read(CHUNK)
            length = 0
            while data:
                length += CHUNK
                data = f.read(CHUNK)
        # 计算duration
        duration = length // (CHANNELS * RATE * 2)
        return duration, length

    def play_pause(self):
        if not self.audio_thread.isRunning():
            self.audio_thread.start()
            self.play_button.setText('暂停')
        else:
            self.audio_thread.pause()
            self.play_button.setText('播放' if self.audio_thread.paused else '暂停')

    def stop(self):
        self.audio_thread.stop()
        self.play_button.setText('播放')

    def update_slider(self, chunk_size):
        new_value = self.slider.value() + chunk_size
        if new_value >= self.slider.maximum():
            new_value = 0

        self.slider.setValue(new_value)
        mins, secs = divmod(new_value // (2 * RATE), 60)
        self.label.setText(f'{mins:02d}:{secs:02d}/{self.max_minutes:02d}:{self.max_seconds:02d}')

# 独立调用示例
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     player = AudioPlayer('documents/audios/ise_audio.pcm')
#     player.show()
#     sys.exit(app.exec_())
