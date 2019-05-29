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


def course_all(cookie, thread_num=5, limit=999999999):
    """
    单线程函数
    下载所有课程信息
    :param cookie: 访问参数
    :param thread_num: 发起网络链接的线程数
    :param limit: 查询页数限制
    :return:
    """
    url = util.kcxx_url
    headers = util.base_headers.copy()
    headers['Cookie'] = cookie
    headers['Referer'] = util.csujwc_url
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    http_data = {
        'PageNum': 1,
        'pageSize': '500'
    }
    http_result = requests.post(url, headers=headers, data=http_data)
    util.print_http_status(http_result, remarks='获取课程信息总表页数')

    # 开始解析网页数据
    soup = BeautifulSoup(http_result.text, "lxml")
    total_pages = int(soup.find(id="totalPages")['value'])
    util.print_i('课程信息总表共%d页' % total_pages)

    # 添加下载页数限制
    if limit < total_pages:
        total_pages = limit

    # 利用多线程加速下载
    page_data = {
        'url': url,
        'headers': headers,
        'pageSize': '500'
    }
    result1 = util.multiprocess(task=course_info, main_data=range(1, total_pages + 1), max_thread=thread_num,
                                attach_data=page_data, multithread=util.nosql_multithread)
    page_data['url'] = util.kcxx2_url
    result2 = util.multiprocess(task=course_info, main_data=range(1, total_pages + 1), max_thread=thread_num,
                                attach_data=page_data, multithread=util.nosql_multithread)
    result = {}
    for item in result1:
        result.setdefault(item['code'], copy.deepcopy(util.course_info))
        result[item['code']]['code'] = item['code']
        result[item['code']]['name'] = item['name']
        result[item['code']]['unit'] = item['unit']
        result[item['code']]['type'] = item['type']
    for item in result2:
        result.setdefault(item['code'], copy.deepcopy(util.course_info))
        result[item['code']]['code'] = item['code']
        result[item['code']]['name'] = item['name']
        result[item['code']]['essence'] = item['essence']
        result[item['code']]['credit'] = item['credit']
    return list(result.values())


def course_info(page_data):
    """
        多线程处理函数
        获取该页码上的所有信息，面向course_info函数提供服务
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
    if page_data['url'] == util.kcxx_url:
        for line in table_list:
            cells = line.find_all('td')
            course_line = copy.deepcopy(util.course_info)
            course_line['code'] = cells[2].string
            course_line['name'] = cells[3].string
            course_line['unit'] = cells[4].string
            course_line['type'] = cells[5].string
            result.append(course_line)
    else:
        for line in table_list:
            cells = line.find_all('td')
            course_line = copy.deepcopy(util.course_info)
            course_line['code'] = cells[2].string
            course_line['name'] = cells[3].string
            course_line['essence'] = cells[4].string
            course_line['credit'] = cells[5].string
            result.append(course_line)
    return result


def course_list(semester, cookie):
    """
    单线程函数
    下载该学期的课程列表信息
    :param semester: 学期信息
    :param cookie: 访问参数
    :return: [{"jx02id": "","kcmc": "","kch": ""}] 表示该学期课程列表
    """
    url = util.tkgl_url
    headers = util.base_headers.copy()
    # 模拟从“行政班级”查询页面而来
    headers['Referer'] = util.qxzbk_url
    headers['Cookie'] = cookie
    payload = {
        'method': 'querykc',
        'xnxqh': semester,
        'kkyx': ''
    }
    for i in range(5):
        http_result = requests.post(url, headers=headers, params=payload)
        if http_result.status_code == 200:
            break

    util.print_http_status(http_result, remarks='取回课程列表 ')

    # 解析获取到的课程列表
    raw_data = http_result.text.replace("{jx02id:", "{'jx02id':")
    raw_data = raw_data.replace(",kcmc:", ",'kcmc':")
    raw_data = raw_data.replace(",kch:", ",'kch':")
    raw_data = raw_data.replace("'", '"')
    raw_data = raw_data.replace(chr(9), '')
    result = json.loads(raw_data)
    return result
