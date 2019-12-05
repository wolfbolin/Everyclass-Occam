# coding=utf-8
import os
import re
import sys
import uuid
import time
import random
import inspect
import hashlib
import platform


# from bs4 import BeautifulSoup

# Print tools

def print_red(message, tag="ERROR"):
    print('\033[0;31m[{}] {}\033[0m'.format(tag, str(message)))  # 红色


def print_green(message, tag="DONE"):
    print('\033[5;32m[{}] {}\033[0m'.format(tag, str(message)))  # 绿色


def print_yellow(message, tag="WARNING"):
    print('\033[0;33m[{}] {}\033[0m'.format(tag, str(message)))  # 黄色


def print_blue(message, tag="BEG"):
    print('\033[0;34m[{}] {}\033[0m'.format(tag, str(message)))  # 深蓝色


def print_purple(message, tag="MID"):
    print('\033[0;35m[{}] {}\033[0m'.format(tag, str(message)))  # 紫色


def print_azure(message, tag="END"):
    print('\033[0;36m[{}] {}\033[0m'.format(tag, str(message)))  # 浅蓝色


def print_white(message, tag="INFO"):
    print('\033[0;37m[{}] {}\033[0m'.format(tag, str(message)))  # 白色


def print_none(message, tag="DEBUG"):
    print('[{}] {}'.format(tag, str(message)))  # 白色


def process_bar(now, total, attach=''):
    # 在窗口底部动态显示进度条
    rate = now / total
    rate_num = int(rate * 100)
    bar_length = int(rate_num / 2)
    blank = ' ' * 100
    if rate_num == 100:
        bar = 'Pid:%5d: %s%s' % (os.getpid(), attach, blank)
        bar = '\r' + bar[0:40]
        bar += '%s>%d%%\n' % ('=' * bar_length, rate_num)
    else:
        bar = 'Pid:%5d: %s%s' % (os.getpid(), attach, blank)
        bar = '\r' + bar[0:40]
        bar += '%s>%d%%' % ('=' * bar_length, rate_num)
    sys.stdout.write(bar)
    sys.stdout.flush()


# Time tools

def unix_time(unit=1):
    return int(time.time() * unit)


def str_time(pattern='%Y-%m-%d %H:%M:%S'):
    return time.strftime(pattern, time.localtime(time.time()))


def format_time(time_obj):
    time_format = "%d-%02d-%02d %02d:%02d"
    time_str = time_format % (time_obj.tm_year, time_obj.tm_mon,
                              time_obj.tm_mday, time_obj.tm_hour, time_obj.tm_min)
    return time_str


def timestamp2unix(v_timestamp):
    return int(time.mktime(v_timestamp.timetuple()))


def unix2timestamp(u_time):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(u_time))


# Calc tools

def func_name(fa=1):
    return inspect.stack()[fa][3]


def random_code():
    return str(uuid.uuid1()).split('-')[0]


def calc_md5(seed):
    seed = str(seed).encode('utf-8')
    md5 = hashlib.md5()
    md5.update(seed)
    return md5.hexdigest()


# def parse_xml(data):
#     xml = re.sub(r'<!\[CDATA\[(.*)\]\]>', lambda m: m.group(1), data)
#     xml = BeautifulSoup(xml, 'lxml')
#     xml = xml.html.body.xml
#     return xml


def cpu_core():
    sys_platform = platform.system()
    if sys_platform == "Windows":
        return int(os.popen("echo %NUMBER_OF_PROCESSORS%").read())
    elif sys_platform == "Linux":
        return int(os.popen(r"cat /proc/cpuinfo | grep 'cpu cores' | uniq | awk '{print $4}'").read())
    else:
        return 0


# File tools


def code_dir():
    file = os.path.abspath(__file__)
    return os.path.dirname(file)


def code_path():
    return os.path.abspath(__file__)


def legalize_name(name):
    legal_name = re.sub(r"[\/\\\:\*\?\"\<\>\|\s']", '_', name)
    legal_name = re.sub(r'[‘’]', '_', legal_name)
    if len(legal_name) == 0:
        return 'null'
    return legal_name


def delete_old_file(dir_path, expire_time):
    time_now = unix_time()
    dir_path = os.path.abspath(dir_path)
    for file in os.listdir(dir_path):
        file_path = '{}/{}'.format(dir_path, file)
        creat_time = os.path.getctime(file_path)
        if time_now > creat_time + expire_time:
            os.remove(file_path)


# Network tools

def parse_cookie(cookies):
    if cookies == "":
        return {}
    cookie_dict = {}
    for line in cookies.split(';'):
        name, value = line.strip().split('=', 1)
        cookie_dict[name] = value
    return cookie_dict


def random_ip(model="all"):
    if model == "A":
        return "%d.%d.%d.%d" % (random.randint(1, 126), random.randint(1, 254),
                                random.randint(1, 254), random.randint(1, 254))
    elif model == "B":
        return "%d.%d.%d.%d" % (random.randint(128, 191), random.randint(1, 254),
                                random.randint(1, 254), random.randint(1, 254))
    elif model == "C":
        return "%d.%d.%d.%d" % (random.randint(192, 223), random.randint(1, 254),
                                random.randint(1, 254), random.randint(1, 254))
    else:
        return "%d.%d.%d.%d" % (random.randint(1, 254), random.randint(1, 254),
                                random.randint(1, 254), random.randint(1, 254))
