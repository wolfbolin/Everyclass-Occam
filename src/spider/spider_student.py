# -*- coding: utf-8 -*-
# Common package
import re
import time
import json
import copy
import requests
from bs4 import BeautifulSoup
# Personal package
import util


def student_all(cookie, thread_num, limit=999999999):
    """
    单线程处理函数
    从common的子页面中获取所有学生的数据信息
    :param cookie: 访问参数
    :param thread_num: 发起网络链接的线程数
    :param limit: 查询页数限制
    :return: 所有学生的详细信息
    """
    url = util.usa_url
    headers = util.base_headers.copy()
    headers['Cookie'] = cookie
    headers['Referer'] = util.csujwc_url
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    http_data = {
        'PageNum': 1,
        'pageSize': '500'
    }
    http_result = requests.post(url, headers=headers, data=http_data)
    util.print_http_status(http_result, remarks='获取学生信息总表页数')

    # 开始解析网页数据
    soup = BeautifulSoup(http_result.text, "lxml")
    total_pages = int(soup.find(id="totalPages")['value'])
    util.print_i('学生信息总表共%d页' % total_pages)

    # 添加下载页数限制
    if limit < total_pages:
        total_pages = limit

    # 利用多线程加速下载
    page_data = {
        'url': url,
        'headers': headers,
        'pageSize': '500'
    }
    result = util.multiprocess(task=student_info, main_data=range(1, total_pages + 1), max_thread=thread_num,
                                    attach_data=page_data, multithread=util.nosql_multithread)
    return result


def student_info(page_data):
    """
    多线程处理函数
    获取该页码上的所有信息，面向student_info函数提供服务
    :param page_data: 访问数据(url ,headers, PageNum, pageSize)
    :return: 该页上的所有信息
    """
    url = page_data['url']
    headers = page_data['headers']
    http_data = {
        'PageNum': page_data['main_data'],
        'pageSize': '500'
    }
    for i in range(5):
        http_result = requests.post(url, headers=headers, data=http_data)
        if http_result.status_code == 200:
            break

        # 开始解析网页数据
    soup = BeautifulSoup(http_result.text, "lxml")
    table_list = soup.find('tbody').contents

    # 循环获取信息
    result = []
    for line in table_list:
        cells = line.find_all('td')
        student_line = copy.deepcopy(util.student_info)
        student_line['code'] = cells[2].string
        student_line['name'] = cells[7].string
        student_line['class'] = cells[4].string
        student_line['deputy'] = cells[5].string
        student_line['campus'] = cells[6].string
        result.append(student_line)
    return result


def student_list(semester, cookie):
    """
    单线程处理函数
    根据学期取回本学期上课的学生列表，每个学期上课的学生列表不相同
    :param semester: 学期 20xx-20xx-x
    :param cookie: 访问参数
    :return: [{"xs0101id": "","xm": "","xh": ""}] 表示该学期学生名单
    """
    url = util.xskb_url
    headers = util.base_headers.copy()
    # 模拟从“行政班级”查询页面而来
    headers['Referer'] = util.csujwc_url
    headers['Cookie'] = cookie
    payload = {
        'xnxq01id': semester,
        'init': 1,
        'isview': 1
    }
    http_result = requests.get(url, headers=headers, params=payload)
    util.print_http_status(http_result, remarks='取回学生列表 ')

    # 解析学生页面中的js常量
    raw_data = re.findall('var bj="(.*?)";', http_result.text, re.S | re.M)[0]
    raw_data = raw_data.replace("{xs0101id:", "{'xs0101id':")
    raw_data = raw_data.replace(",xm:", ",'xm':")
    raw_data = raw_data.replace(",xh:", ",'xh':")
    raw_data = raw_data.replace("'", '"')
    raw_data = raw_data.replace("\t", "")  # 个别学生姓名中
    raw_data = raw_data.replace("\n", "")  # 包含不可见字符
    raw_data = raw_data.replace(" ", "")  # 影响json解析
    result = json.loads(raw_data)
    return result


def student_table(data_set):
    """
    多线程处理函数
    下载学生的课表并缓存至文件夹中
    :param data_set: 学期+学生信息{"xs0101id":"","xm":"","xh":""}+访问参数
    """
    cookie = data_set['cookie']
    semester = data_set['semester']
    # 准备下载数据
    url = util.kbkb_url
    headers = util.base_headers.copy()
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    headers['Referer'] = util.xskb_url
    headers['Cookie'] = cookie
    http_data = {
        'type': 'xs0101',
        'isview': '0',
        'zc': '',
        'xnxq01id': semester,
        'xs0101id': data_set['xs0101id'],
        'xs': data_set['xm'],  # 学生信息中表现为xm(姓名)
        'sfFD': '1'
    }
    # 开始下载数据
    for i in range(5):
        time.sleep(2)
        http_result = requests.post(url, headers=headers, data=http_data)
        if http_result.status_code == 200:
            break

    # 不解析数据直接储存
    util.save_to_cache(semester, 'student_html', data_set['xh'], http_result.text)
    return []
