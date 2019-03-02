# -*- coding: utf-8 -*-
# Common package
import json
import copy
import requests
from bs4 import BeautifulSoup
# Personal package
import util


def teacher_all(cookie, thread_num, limit=999999999):
    """
    单线程处理函数，内置多线程操作
    从Common的子页面中获取所有教师的数据信息
    :param cookie: 访问参数
    :param thread_num: 发起网络链接的线程数
    :param limit: 查询页数限制
    :return: 所有老师的详细信息
    """
    url = util.jgs_url
    headers = util.base_headers.copy()
    headers['Cookie'] = cookie
    headers['Referer'] = util.csujwc_url
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    http_data = {
        'PageNum': 1,
        'pageSize': '500'
    }
    http_result = requests.post(url, headers=headers, data=http_data)
    util.print_http_status(http_result, remarks='获取教师信息总表页数')

    # 开始解析网页数据
    soup = BeautifulSoup(http_result.text, "lxml")
    total_pages = int(soup.find(id="totalPages")['value'])
    util.print_i('教师信息总表共%d页' % total_pages)

    # 添加下载页数限制
    if limit < total_pages:
        total_pages = limit

    # 利用多进程加速下载
    page_data = {
        'url': url,
        'headers': headers,
        'pageSize': '500'
    }
    result = util.multiprocess(task=teacher_info, main_data=range(1, total_pages + 1), max_thread=thread_num,
                               attach_data=page_data, multithread=util.nosql_multithread)
    return result


def teacher_info(page_data):
    """
    多线程处理函数
    获取该页码上的所有信息，面向teacher_all函数提供服务
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
        http_result = requests.post(url, data=http_data, headers=headers)
        if http_result.status_code == 200:
            break

    # 开始解析网页数据
    soup = BeautifulSoup(http_result.text, "lxml")
    table_list = soup.find('tbody').contents

    # 循环获取信息
    result = []
    for line in table_list:
        cells = line.find_all('td')
        teacher_line = copy.deepcopy(util.teacher_info)
        teacher_line['code'] = cells[3].string
        teacher_line['name'] = cells[2].string
        teacher_line['unit'] = cells[4].string
        teacher_line['title'] = cells[6].string
        teacher_line['degree'] = cells[7].string
        result.append(teacher_line)
    return result


def teacher_list(semester, cookie):
    """
    单线程处理函数
    从各类课表查询页面中查询本学期上课教师列表
    :param semester: 学期 20xx-20xx-x
    :param cookie: 访问参数
    :return: [{jg0101id:'',jgxm:''}] 表示教师列表
    """
    url = util.pklb_url
    headers = util.base_headers.copy()
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    headers['Referer'] = util.sykb_url
    headers['Cookie'] = cookie
    payload = {
        'method': 'queryjg0101',
        'xnxq01id': semester,
        'yxbh': '',
        'jszwdm': ''
    }
    http_result = requests.post(url, headers=headers, params=payload)
    util.print_http_status(http_result, remarks='取回本学期教师列表')

    # 解析获取到的教师列表
    raw_data = http_result.text.replace("{jg0101id:", "{'jg0101id':")
    raw_data = raw_data.replace(",jgh:", ",'jgh':")
    raw_data = raw_data.replace(",xm:", ",'xm':")
    raw_data = raw_data.replace("'", '"')
    result = json.loads(raw_data)
    return result


def teacher_table(data_set):
    """
    多线程处理函数
    下载教师的课表列表并缓存至文件夹中
    :param data_set: 学期+教师信息 {jg0101id: '', jgh: '', xm: ''}+访问参数
    """
    cookie = data_set['cookie']
    semester = data_set['semester']
    teacher_code = data_set['jgh']
    # 准备下载数据
    url = util.kbkb_url
    headers = util.base_headers.copy()
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    headers['Referer'] = util.sykb_url
    headers['Cookie'] = cookie
    # teacherID为教工姓名，不是教工号
    http_data = {
        'type': 'jg0101',
        'isview': '0',
        'zc': '',
        'xnxq01id': semester,
        'yxbh': '',
        'jszwdm': '',
        'teacherID': data_set['xm'],
        'jg0101id': data_set['jg0101id'],
        'jg0101mc': ''
    }
    # 开始下载数据
    for i in range(5):
        http_result = requests.post(url, headers=headers, data=http_data)
        if http_result.status_code == 200:
            break

    # 不解析数据直接储存
    teacher_code = teacher_code.replace('*', '#')  # 临时改变名称，避免文件系统限制
    util.save_to_cache(semester, 'teacher_html', teacher_code, http_result.text)
    return []
