# -*- coding: utf-8 -*-
# Common package
import os
import sys
import time

"""
被其他运行包所引用的工具包
提供了大部分常用功能
"""


# 自定义异常
class ErrorSignal(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def print_e(message):
    print('\033[0;31;0m[ERROR] {}\033[0m'.format(str(message)))


def print_d(message):
    print('\033[0;32;0m[DONE] {}\033[0m'.format(str(message)))


def print_w(message):
    print('\033[0;33;0m[WARNING] {}\033[0m'.format(str(message)))


def print_a(message):
    print('\033[0;34;0m[ACTION] {}\033[0m'.format(str(message)))


def print_t(message):
    print('\033[0;36;0m[TIPS] {}\033[0m'.format(str(message)))


def print_i(message):
    print('\033[0;37;0m[INFO] {}\033[0m'.format(str(message)))


def process_bar(now, total, attach=''):
    # 在窗口底部动态显示进度条
    rate = now / total
    rate_num = int(rate * 100)
    bar_length = int(rate_num / 2)
    blank = '                                                    '
    if rate_num == 100:
        bar = 'Pid:%5d:%s%s' % (os.getpid(), attach, blank)
        bar = '\r' + bar[0:30]
        bar += '%s>%d%%\n' % ('=' * bar_length, rate_num)
    else:
        bar = 'Pid:%5d:%s%s' % (os.getpid(), attach, blank)
        bar = '\r' + bar[0:30]
        bar += '%s>%d%%' % ('=' * bar_length, rate_num)
    sys.stdout.write(bar)
    sys.stdout.flush()


def print_data_size(data, remarks=''):
    # 展示变量当前内存消耗状态
    print_i('{}消耗内存{}kb'.format(remarks, sys.getsizeof(data) / 1024))


def print_http_status(result, remarks=''):
    # 展示网络请求地址与状态，另有附加信息可选
    if result.status_code == 200 or result.status_code == 302:
        print_i('%s HTTP状态%d url=%s' % (remarks, result.status_code, result.url))
    else:
        print_e('%s HTTP状态%d url=%s' % (remarks, result.status_code, result.url))
        raise ErrorSignal("网络连接异常或失败，请重试")


def save_to_log(name, data):
    # 将需要存储的日志数据储存在文件中
    time_now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    log_file_name = './cache/log/%s' % (name + time_now)
    with open(log_file_name, 'w', encoding='utf8') as file:
        file.write(str(data))
    print_t('日志已被存储至 ' + log_file_name)


def save_to_output(name, data):
    # 将调试需要的数据储存在文件中
    time_now = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    output_file_name = './cache/output/%s' % (name + time_now)
    with open(output_file_name, 'w', encoding='utf8') as file:
        file.write(str(data))
    print_t('数据已被存储至 ' + output_file_name)


def save_to_cache(semester, folder, name, data):
    # 将获取到的数据缓存至本地，减少数据操作失败后的网络下载时间
    if folder != '':
        cache_file_name = './cache/%s/%s/%s' % (semester, folder, name)
    else:
        cache_file_name = './cache/%s/%s' % (semester, name)
    with open(cache_file_name, 'w', encoding='utf8') as file:
        data = str(data)
        if sys.getsizeof(data) < 104857600:
            file.write(data)
        else:
            for i in range(0, len(data), 4096):
                file.write(data[i: i + 4096])

    # print_i('数据已缓存至 ' + cache_file_name)


def del_from_cache(semester, folder, name):
    # 删除本地的数据缓存，此操作可避免软件读取到错误的缓存
    if folder != '':
        cache_file_name = './cache/%s/%s/%s' % (semester, folder, name)
    else:
        cache_file_name = './cache/%s/%s' % (semester, name)
    if os.path.exists(cache_file_name) is False:
        raise ErrorSignal('文件不存在，请检查本地缓存')
    os.remove(cache_file_name)


def query_from_cache(semester, folder, name):
    # 检查本地缓存是否存在，没有提示
    if folder != '':
        cache_file_name = './cache/%s/%s/%s' % (semester, folder, name)
    else:
        cache_file_name = './cache/%s/%s' % (semester, name)
    if os.path.exists(cache_file_name) is True:
        return True
    else:
        return False


def read_from_cache(semester, folder, name):
    # 读取本地的数据缓存，减少数据操作失败后的网络下载时间
    if folder != '':
        cache_file_name = './cache/%s/%s/%s' % (semester, folder, name)
    else:
        cache_file_name = './cache/%s/%s' % (semester, name)
    if os.path.exists(cache_file_name) is False:
        raise ErrorSignal('文件不存在，请检查本地缓存')
    with open(cache_file_name, 'r', encoding='utf8') as file:
        data = file.read()
    return data


def get_config(key):
    """
    自动从环境变量或配置文件中获取设定的信息
    :param key: 环境变量键值
    :return: 预定义的环境变量值或None
    """
    env_dict = os.environ
    try:
        from .config import set_dict
    except ImportError:
        set_dict = {}
    if key in env_dict:
        return env_dict[key]
    elif key in set_dict:
        return set_dict[key]
    else:
        return None
