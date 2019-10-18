# coding=utf-8
import util
import requests


# 获取数据访问权限Cookie
def cookie(configs):
    # 尝试访问教务网首页
    # 在该过程中将获取访问过程中的cookie信息
    url = configs.JW_INDEX
    headers = util.fake_header('html', url)
    result = requests.get(url, headers=headers)
    cookies = result.cookies.get_dict()
    cookie_str = ''
    for key in cookies:  # 合成cookie字符串
        cookie_str += key + '=' + cookies[key] + ';'
    util.print_http_status(result, '访问教务主页')

    # 通过cas认证获取数据访问权限
    # 在该过程中不产生cookie，服务器将依赖SESSION赋予用户数据访问权限
    url = configs.KB_LOGIN
    headers = util.fake_header('html', url)
    headers['Referer'] = configs.JW_INDEX
    headers['Cookie'] = cookie_str
    http_result = requests.get(url, headers=headers, allow_redirects=False)
    util.print_http_status(http_result, '获取教务鉴权')

    return cookie_str
