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
