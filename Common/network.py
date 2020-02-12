# coding=utf-8
import os
import Util
import Config
from urllib import parse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

useragent_path = os.path.dirname(__file__) + '/fake_useragent.json'


def generate_http_headers():
    rand_ip = Util.random_ip("A")
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Host': "",
        'Referer': "",
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Proxy-Connection': 'keep-alive',
        'CLIENT-IP': rand_ip,
        'REMOTE_ADDR': rand_ip,
        'HTTP_CLIENT_IP': rand_ip,
        'HTTP_X_FORWARDED_FOR': rand_ip,
        'User-Agent': UserAgent(path=useragent_path).random,
    }
    return headers


def modify_mask_ip(headers):
    rand_ip = Util.random_ip("A")
    headers["CLIENT-IP"] = rand_ip
    headers["REMOTE_ADDR"] = rand_ip
    headers["HTTP_CLIENT_IP"] = rand_ip
    headers["HTTP_X_FORWARDED_FOR"] = rand_ip
    return headers


def modify_mask_ua(headers):
    headers["User-Agent"] = UserAgent(path=useragent_path).random


def modify_mask_host(headers, url):
    url_obj = parse.urlparse(url)
    headers["Host"] = url_obj.netloc
    return headers


def modify_mask_cookies(headers, cookies):
    cookie_str = ''
    for key in cookies:  # 合成cookie字符串
        cookie_str += key + '=' + cookies[key] + ';'
    headers['Cookie'] = cookie_str
    return headers


def auth_cookie(config):
    headers = generate_http_headers()

    # 尝试访问教务网首页
    url = config["url"]["csujwc"]
    headers = modify_mask_host(headers, url)
    _, cookies = Util.http_request("GET", url, keep_cookie=True, headers=headers, proxies=config["proxy"])
    headers = modify_mask_cookies(headers, cookies)
    headers["Referer"] = url

    # 通过cas认证获取数据访问权限
    url = config["url"]['kblogin']
    headers = modify_mask_host(headers, url)
    res = Util.http_request("GET", url, headers=headers, proxies=config["proxy"])

    return headers, cookies


if __name__ == '__main__':
    _config = Config.load_config("../Config")
    print(auth_cookie(_config))
