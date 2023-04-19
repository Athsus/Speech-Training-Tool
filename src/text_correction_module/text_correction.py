"""

讯飞开放平台
语法纠正web api调用


"""
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests

APPId = "127aa6c2"
APISecret = "YTY0ZTI5ZGZlYjNmNTQ4NDA5OWRjMWRl"
APIKey = "a1ed716096e65662538dc24e6e532d03"

error_translation = {
    "pol": "政治术语纠错",
    "char": "别字纠错",
    "word": "别词纠错",
    "redund": "语法纠错-冗余",
    "miss": "语法纠错-缺失",
    "order": "语法纠错-乱序",
    "dapei": "搭配纠错",
    "punc": "标点纠错",
    "idm": "成语纠错",
    "org": "机构名纠错",
    "leader": "领导人职称纠错",
    "number": "数字纠错",
    "addr": "地名纠错",
    "name": "全文人名纠错",
    "grammar_pc": "句式杂糅&语义重复",
}



class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


class TextCorrection:
    def __init__(self, Text):
        self.appid = APPId
        self.apisecret = APISecret
        self.apikey = APIKey
        self.text = Text
        self.url = 'https://api.xf-yun.com/v1/private/s9a87e3ec'

    # calculate sha256 and encode to base64
    def sha256base64(self, data):
        sha256 = hashlib.sha256()
        sha256.update(data)
        digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
        return digest

    def parse_url(self, requset_url):
        stidx = requset_url.index("://")
        host = requset_url[stidx + 3:]
        schema = requset_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise AssembleHeaderException("invalid request url:" + requset_url)
        path = host[edidx:]
        host = host[:edidx]
        u = Url(host, path, schema)
        return u

    # build websocket auth request url
    def assemble_ws_auth_url(self, requset_url, method="POST", api_key="", api_secret=""):
        u = self.parse_url(requset_url)
        host = u.host
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        # print(date)
        # date = "Thu, 12 Dec 2019 01:57:27 GMT"
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        # print(signature_origin)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # print(authorization_origin)
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }

        return requset_url + "?" + urlencode(values)

    def get_body(self):
        body = {
            "header": {
                "app_id": self.appid,
                "status": 3,
                # "uid":"your_uid"
            },
            "parameter": {
                "s9a87e3ec": {
                    # "res_id":"your_res_id",
                    "result": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "input": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 3,
                    "text": base64.b64encode(self.text.encode("utf-8")).decode('utf-8')
                }
            }
        }
        return body

    def get_result(self):
        """IflyTek api"""
        request_url = self.assemble_ws_auth_url(self.url, "POST", self.apikey, self.apisecret)
        headers = {'content-type': "application/json", 'host': 'api.xf-yun.com', 'app_id': self.appid}
        body = self.get_body()
        response = requests.post(request_url, data=json.dumps(body), headers=headers)
        print('onMessage：\n' + response.content.decode())
        tempResult = json.loads(response.content.decode())
        res = base64.b64decode(tempResult['payload']['result']['text']).decode()
        # print('text字段解析：\n' + res)
        res = json.loads(res)
        return res

    def parse_result(self, result: dict) -> str:
        """
        todo 转移过来比较好
        解析一个result
        其中的Key为（前者的key，比如pol是"pol"，后者是其“解释意义”）
        pol 政治术语纠错
        char 别字纠错
        word 别词纠错
        redund 语法纠错-冗余
        miss 语法纠错-缺失
        order 语法纠错-乱序
        dapei 搭配纠错
        punc 标点纠错
        idm 成语纠错
        org 机构名纠错
        leader 领导人职称纠错
        number 数字纠错
        addr 地名纠错
        name 全文人名纠错
        grammar_pc 句式杂糅 &语义重复

        其中，每个key的value是一个list，形如：
        [10, '画蛇天足', ‘画蛇添足’, 'idm' ]
        (出现的index, 原成语, 纠正成语, 语法错误种类(此处是成语错误idm))

        :return: 输出返回一个一个HTML格式的字符串，
        最终会设置在pyqt5组件的textEdit中，self.text是完整的文章，通过result的内容设置为，错误的内容（错别字，错别词等）标黄，并且鼠标放在这个位置会在其旁边跳出框，显示对应的”解释意义“。

        parse ref doc: https://www.xfyun.cn/doc/nlp/textCorrection/API.html#%E8%BF%94%E5%9B%9E%E7%BB%93%E6%9E%9C
        """
        pass


# 单独调用示例
if __name__ == '__main__':
    Text = "衣据，鱿鱼圈，战士，画蛇天足，足不初户，狐假唬威，威风凛领，轮到"

    demo = TextCorrection(Text)
    result = demo.get_result()  # demo的获得res
    print("?")
