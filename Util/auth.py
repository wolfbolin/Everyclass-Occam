# coding=utf-8
import Util
import requests


def auth_cookie(config):
    # 尝试访问教务网首页
    url = config["url"]["csujwc"]
    headers = Util.access_header(url)
    result, cookie = Util.safe_http_request("GET", url, headers=headers, proxies=config["proxy"])

    if result is None:
        Util.print_red("Get cookie failed. Please check network.")
        return None

    # 通过cas认证获取数据访问权限
    url = config["url"]['kblogin']
    headers = Util.access_header(url)
    headers['Referer'] = config["url"]["csujwc"]
    Util.safe_http_request("GET", url, headers=headers, cookies=cookie, proxies=config["proxy"], allow_redirects=False)

    return cookie


if __name__ == '__main__':
    _config = Util.get_config("../config")
    Util.print_none(auth_cookie(_config))
