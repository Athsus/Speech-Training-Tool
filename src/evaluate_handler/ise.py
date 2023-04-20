"""

讯飞开放平台
语音评测web api流式调用

doc: https://www.xfyun.cn/doc/Ise/IseAPI.html#%E6%8E%A5%E5%8F%A3%E8%A6%81%E6%B1%82
"""
import sys
from builtins import Exception, str, bytes

import numpy as np
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread

import xmltodict as xmltodict
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from matplotlib import pyplot as plt
from pylab import mpl

# 设置中文显示字体
from websocket import WebSocketConnectionClosedException

mpl.rcParams["font.sans-serif"] = ["SimHei"]

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

APP_ID = "127aa6c2"
API_KEY = "a1ed716096e65662538dc24e6e532d03"
API_SECRET = "YTY0ZTI5ZGZlYjNmNTQ4NDA5OWRjMWRl"

#  BusinessArgs参数常量
SUB = "ise"
ENT = "cn_vip"
# 中文题型：read_syllable（单字朗读，汉语专有）read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)
# 英文题型：read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)simple_expression（英文情景反应）read_choice（英文选择题）topic（英文自由题）retell（英文复述题）picture_talk（英文看图说话）oral_translation（英文口头翻译）
CATEGORY = "read_chapter"


# 待评测文本 utf8 编码，需要加utf8bom 头

# 直接从文件读取的方式
# TEXT = '\uFEFF'+ open("cn/read_sentence_cn.txt","r",encoding='utf-8').read()



class IFlytekISE(QThread):

    emit_res = pyqtSignal(dict)

    # 初始化
    def __init__(self, _text):
        global text
        super().__init__()
        text = '\uFEFF' + _text
        websocket.enableTrace(False)

    # 生成url
    def create_url(self):
        # wws请求对Python版本有要求，py3.7可以正常访问，如果py版本请求wss不通，可以换成ws请求，或者更换py版本
        url = 'ws://ise-api.xfyun.cn/v2/open-ise'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ise-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/open-ise " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(API_SECRET.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            API_KEY, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ise-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)

        # 此处打印出建立连接时候的url,参考本demo的时候，比对相同参数时生成的url与自己代码生成的url是否一致
        print("date: ", date)
        print("v: ", v)
        print('websocket url :', url)
        return url

    def run(self):
        wsUrl = self.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        # 把res和text emit出去, sub process不要弹出窗口
        self.return_results()


    def return_results(self):
        ret = {
            "result": res,
            "text": text
        }
        if res is None:
            print("ise failed")
            self.emit_res.emit({})
        else:
            self.emit_res.emit(ret)


text = None
res = None


# 收到websocket消息的处理
def on_message(ws, message):
    global res
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]
            status = data["status"]
            result = data["data"]
            if (status == 2):
                xml = base64.b64decode(result)
                # python在windows上默认用gbk编码，print时需要做编码转换，mac等其他系统自行调整编码
                xml_dict = xmltodict.parse(xml.decode("gbk"))
                res = xml_dict


    except Exception as e:
        print("receive msg,but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        CommonArgs = {"app_id": APP_ID}
        BusinessArgs = {"category": CATEGORY, "sub": SUB, "ent": ENT, "cmd": "ssb", "auf": "audio/L16;rate=16000",
                        "aue": "raw", "text": text, "ttp_skip": True, "aus": 1}
        frameSize = 1280  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open("documents/audios/ise_audio.pcm", "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                if not buf:
                    status = STATUS_LAST_FRAME
                if status == STATUS_FIRST_FRAME:
                    d = {"common": CommonArgs,
                         "business": BusinessArgs,
                         "data": {"status": 0}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"business": {"cmd": "auw", "aus": 2, "aue": "raw"},
                         "data": {"status": 1, "data": str(base64.b64encode(buf).decode())}}
                    ws.send(json.dumps(d))
                elif status == STATUS_LAST_FRAME:
                    d = {"business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                         "data": {"status": 2, "data": str(base64.b64encode(buf).decode())}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)

        ws.close()
        print("ise ws closed")

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 评测文本

    text = "就是没我觉得这再加点内容"
    audio_path = "documents/audios/ise_audio.pcm"
    # 评测音频
    now = IFlytekISE(text)
    now.run()