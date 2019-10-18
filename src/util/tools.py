# coding=utf-8
import os
import util
from urllib import parse
from fake_useragent import UserAgent


# 自定义异常
class ErrorSignal(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def fake_header(x_type="html", url=""):
    useragent_path = os.path.dirname(__file__) + '/fake_useragent.json'
    user_agent = UserAgent(path=useragent_path).random
    header = {
        'Host': parse.urlparse(url).netloc,
        'Accept': 'text/html, */*',
        'Connection': 'keep-alive',
        'User-Agent': user_agent,
        'Cache-Control': 'no-cache',
        'Accept-Encoding': 'gzip, deflate'
    }
    if x_type == 'json':
        header['Content-Type'] = 'application/json'
        return header
    elif x_type == 'html':
        return header
    return None


def print_http_status(result, remarks=''):
    # 展示网络请求地址与状态，另有附加信息可选
    if result.status_code == 200 or result.status_code == 302:
        util.print_done('%s HTTP状态%d url=%s' % (remarks, result.status_code, result.url))
    else:
        util.print_error('%s HTTP状态%d url=%s' % (remarks, result.status_code, result.url))
        raise ErrorSignal("网络连接异常或失败，请重试")
