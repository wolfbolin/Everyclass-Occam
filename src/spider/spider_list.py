# coding=utf-8
import os
import util
import pymysql
import requests
from bs4 import BeautifulSoup


# 从Common的子页面中获取所有教师的数据信息
def pull_teacher_list(configs, cookie):
    url = configs.JS_LIST
    headers = util.fake_header('html', url)
    headers['Cookie'] = cookie
    headers['Referer'] = configs.JW_INDEX
    headers['Origin'] = 'http://csujwc.its.csu.edu.cn'
    http_data = {
        'PageNum': 1,
        'pageSize': '500'
    }
    http_result = requests.post(url, headers=headers, data=http_data)
    util.print_http_status(http_result, remarks='获取教师列表页数')

    # 开始解析网页数据
    soup = BeautifulSoup(http_result.text, "lxml")
    total_pages = int(soup.find(id="totalPages")['value'])
    util.print_info('教师信息总表共%d页' % total_pages)

    # 利用多进程加速下载
    page_data = {
        'url': url,
        'headers': headers,
        'pageSize': '500'
    }
    result = util.multiprocess(configs, test_task, util.simple_multithread, ['1', '1', '1', '1', '1', '1', ], None)
    return result


