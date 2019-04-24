# -*- coding: utf-8 -*-
# Common package
import re
import json
import time
from hashlib import md5
from bs4 import BeautifulSoup
# Personal package
import util


def course_list(data_set):
    """
    单线程处理函数
    完成对课程相关信息的数据校验
    :param data_set: 所有课程信息
    :return: rowcount
    """
    for student in data_set:
        try:
            student['jx02id'] = student['jx02id'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            student['kcmc'] = student['kcmc'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            student['kch'] = student['kch'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            student['code'] = student['kch']
            student['name'] = student['kcmc']
        except TypeError as e:
            raise util.ErrorSignal('学生{}缺少字段'.format(student))
    return data_set

