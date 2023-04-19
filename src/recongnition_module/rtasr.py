"""

讯飞开放平台
实时语音转写web api流式调用

doc: https://www.xfyun.cn/doc/asr/rtasr/API.html
"""
import hashlib
import hmac

import websocket
import pyaudio
import time
import json
import base64
import threading
import requests
from urllib.parse import quote

from PyQt5.QtCore import QThread, pyqtSignal
from websocket import create_connection

APP_ID = "127aa6c2"
API_KEY = "ceebe3fcab3432ef97e4573fdcf4fdf9"
API_SECRET = "YTY0ZTI5ZGZlYjNmNTQ4NDA5OWRjMWRl"

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 60


class IFlytekRTASR(QThread):

    emit_res = pyqtSignal(str)

    def __init__(self, text_browser=None):
        super().__init__()
        self.frames = []
        self.text_browser = text_browser


    def connect(self):
        """
        voice init
        :return:
        """
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                      rate=RATE, input=True, frames_per_buffer=CHUNK)
        # encrypt
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (APP_ID + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = API_KEY.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        self.end_tag = "{\"end\": true}"
        self.ws = create_connection(base_url + "?appid=" + APP_ID + "&ts=" + ts + "&signa=" + quote(signa) + "&vadMdn=2")
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def run(self):
        self.connect()
        index = 1
        self.frames = []
        try:
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                chunk = self.stream.read(CHUNK)
                if not chunk:
                    break
                self.frames.append(chunk)
                self.ws.send(chunk)
                index += 1
                time.sleep(0.04)
        except Exception as e:
            print(e)
            print("receive result end")


    def recv(self):
        try:
            # pre_message = ""
            while self.ws.connected:
                result = str(self.ws.recv())
                if len(result) == 0:
                    print("receive result end")
                    break
                result_dict = json.loads(result)
                # 解析结果
                if result_dict["action"] == "started":
                    print("handshake success, result: " + result)

                if result_dict["action"] == "result":
                    data = json.loads(result_dict["data"])["cn"]["st"]
                    data_type = data["type"]

                    if data_type == '0':
                        data_rt = data["rt"]
                        st = []
                        for item in data_rt[0]["ws"]:
                            st.append(item["cw"][0]["w"])
                        print(f"实时转写结果: {''.join(st)}")
                        self.text_browser.insertPlainText(''.join(st))
                if result_dict["action"] == "error":
                    print("rtasr error: " + result)
                    self.ws.close()
                    return
        except websocket.WebSocketConnectionClosedException:
            print("receive result end")

    def close(self):
        try:
            print("closing")
            if hasattr(self, 'ws') and self.ws.connected:
                self.ws.send(bytes(self.end_tag.encode('utf-8')))  # send end tag
                self.ws.close()  # close ws

            if hasattr(self, 'stream') and self.stream.is_active():
                self.stream.stop_stream()  # pause
                self.stream.close()  # close

            if hasattr(self, 'audio'):
                self.audio.terminate()  # terminate audio

            path = "documents/audios/ise_audio.pcm"
            with open(path, "wb") as pcmfile:
                pcmfile.write(b''.join(self.frames))
            print("closed")
        except Exception as e:
            pass
