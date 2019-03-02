# -*- coding: utf-8 -*-
# Common package
import copy
import requests
from bs4 import BeautifulSoup
# Personal package
import util


def cookie():
    """
    单线程函数
    获取数据访问权限,各种课表的权限是一致的
    :return: 字符串，具有访问权限的cookie信息
    """
    # 尝试访问教务网首页
    # 在该过程中将获取访问过程中的cookie信息
    url = util.csujwc_url
    headers = util.base_headers.copy()
    result = requests.get(url, headers=headers)
    cookies = result.cookies.get_dict()
    cookie_str = ''
    for key in cookies:  # 合成cookie字符串
        cookie_str += key + '=' + cookies[key] + ';'
    util.print_http_status(result)

    # 通过cas认证获取数据访问权限
    # 在该过程中不产生cookie，服务器将依赖SESSION赋予用户数据访问权限
    # 该过程不可缺少，状态码应为302，转向参数'f'指向的链接
    url = util.kblogin_url
    headers = util.base_headers.copy()
    headers['Referer'] = util.csujwc_url
    headers['Cookie'] = cookie_str
    http_result = requests.get(url, headers=headers, allow_redirects=False)
    util.print_http_status(http_result)  # 状态码应返回302

    # 将获取并注册过的cookie作为字符串返回
    return cookie_str


def room_all(cookies):
    """
    单线程处理函数
    获取所有教室信息
    :return: 学校教室数据
    """
    # 大约有一千个教室，自适应页数
    result = []
    page_num = 0
    change_flag = True
    url = util.jspk_url
    headers = util.base_headers.copy()
    headers['Cookie'] = cookies
    headers['Referer'] = util.csujwc_url
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    while change_flag:
        change_flag = False
        page_num += 1
        http_data = {
            'PageNum': page_num,
            'pageSize': '500'
        }
        for i in range(5):
            http_result = requests.post(url, data=http_data, headers=headers)
            if http_result.status_code == 200:
                break

        # 开始解析网页数据
        soup = BeautifulSoup(http_result.text, "lxml")
        table_list = soup.find('tbody').contents
        # 循环获取信息
        for line in table_list:
            cells = line.find_all('td')
            room_line = copy.deepcopy(util.room_info)
            room_line['campus'] = cells[2].string
            room_line['building'] = cells[3].string
            room_line['code'] = cells[4].string
            room_line['name'] = cells[5].string
            result.append(room_line)
            change_flag = True
    return result
