# coding=utf-8
import os
import sys


def print_error(message):
    print('\033[0;31m[ERROR] {}\033[0m'.format(str(message)))  # 红色


def print_done(message):
    print('\033[5;32m[DONE] {}\033[0m'.format(str(message)))  # 绿色


def print_warning(message):
    print('\033[0;33m[WARNING] {}\033[0m'.format(str(message)))  # 黄色


def print_begin(message):
    print('\033[0;34m[BEG] {}\033[0m'.format(str(message)))  # 深蓝色


def print_middle(message):
    print('\033[0;35m[MID] {}\033[0m'.format(str(message)))  # 紫色


def print_end(message):
    print('\033[0;36m[END] {}\033[0m'.format(str(message)))  # 浅蓝色


def print_info(message):
    print('\033[0;37m[INFO] {}\033[0m'.format(str(message)))  # 白色


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
