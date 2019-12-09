# coding=utf-8
import os
import Util
import requests
from urllib import parse
from fake_useragent import UserAgent

useragent_path = os.path.dirname(__file__) + '/fake_useragent.json'


class Cookies:
    def __init__(self):
        rand_ip = Util.random_ip("A")
        self.cookies = {}
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Host': "",
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'Proxy-Connection': 'keep-alive',
            'User-Agent': UserAgent(path=useragent_path).random,
        }

    def get_headers(self):
        return self.headers

    def get_cookies(self):
        return self.cookies

    def set_url(self, url):
        url_obj = parse.urlparse(url)
        self.headers["Host"] = url_obj.netloc
        return self

    def reset_ip(self, model="A"):
        rand_ip = Util.random_ip(model)
        self.headers["CLIENT-IP"] = rand_ip
        self.headers["HTTP_X_FORWARDED_FOR"] = rand_ip

        return self

    def reset_ua(self):
        self.headers["User-Agent"] = UserAgent(path=useragent_path).random
        return self

    def auth_cookies(self, config):
        # 尝试访问教务网首页
        url = config["url"]["csujwc"]
        self.set_url(url)
        result, cookies = Util.safe_http_request("GET", url, headers=self.headers, proxies=config["proxy"])

        if result is None:
            Util.print_red("Get cookie failed. Please check network.")
            return None

        # 通过cas认证获取数据访问权限
        url = config["url"]['kblogin']
        self.set_url(url)
        self.headers['Referer'] = config["url"]["csujwc"]
        Util.safe_http_request("GET", url, headers=self.headers, cookies=cookies, proxies=config["proxy"],
                               allow_redirects=False)
        self.cookies = cookies
        return self


if __name__ == '__main__':
    _config = Util.get_config("../config")
    cookies = Cookies()
    cookies.auth_cookies(_config)
    Util.print_none(cookies.get_cookies())
