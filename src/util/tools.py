# -*- coding: utf-8 -*-
# Common package
# Personal package
import util

"""
向内部业务提供特殊的通用性工具
"""


def read_week(time_str):
    """
    将教务系统中复杂的周次信息读取为数组
    例如将 ‘1,5-9,11-15/单周’ 变为 [1,5,7,9,11,13,15]
    :param time_str: 教务系统中的时间编号
    :return: 转化后的数组
    """
    # 排除双横杠的异常字符串 例如：4--5,7-18/全周
    time_str = time_str.replace('--', '-')
    length = time_str.split('/')[0]
    try:
        cycle = time_str.split('/')[1]
    except IndexError as ie:
        cycle = 0

    if cycle == '单周' or cycle == '单':
        cycle = 1
    elif cycle == '双周' or cycle == '双':
        cycle = 2
    else:
        cycle = 0

    week = []
    try:
        for part in length.split(','):
            point = part.split('-')
            if len(point) == 1:  # 说明没有时间跨度
                if len(point[0]) == 0:
                    continue
                week.append(int(point[0]))
            else:  # 说明具有时间跨度
                for t in range(int(point[0]), int(point[1]) + 1):
                    if cycle == 0:
                        week.append(int(t))
                    elif cycle == 1 and t % 2 == 1:
                        week.append(int(t))
                    elif cycle == 2 and t % 2 == 0:
                        week.append(int(t))
    except ValueError as e:
        util.print_e('奇怪的时间信息：{}'.format(time_str))
    week.sort()
    return week


def make_week(time_list):
    """
    将周次信息合并为方便理解的中文字符串
    :param time_list: 周次列表
    :return: 简化的周次信息
    """
    # 自带去重排序效果（仅增强健壮性，不可依赖）
    time_list = list(set(time_list))
    # 判断异常
    if len(time_list) == 0:
        raise util.ErrorSignal('发现了没有周次的课程')
    # 判断一周的课程
    if len(time_list) == 1:
        return '%d/全周' % time_list[0]
    # 判断单双全周
    dt = []
    for i in range(1, len(time_list)):
        dt.append(time_list[i] - time_list[i - 1])
    dt = list(set(dt))
    if len(dt) == 1:  # 说明周次是有规律的
        if dt[0] == 1:  # 说明是全周课程
            return '%d-%d/全周' % (time_list[0], time_list[-1])
        if dt[0] == 2 and time_list[0] % 2 == 1:  # 说明是单周
            return '%d-%d/单周' % (time_list[0], time_list[-1])
        if dt[0] == 2 and time_list[0] % 2 == 0:  # 说明是双周
            return '%d-%d/双周' % (time_list[0], time_list[-1])
    # 不能进行单双全周聚合的时间
    time_list.append(999)  # 添加不可能存在的周次推动最后一组数据进入结果
    begin = time_list[0]
    result = ''
    for i in range(1, len(time_list)):
        if time_list[i] != time_list[i - 1] + 1:  # 说明时间发生了不连续的情况
            if time_list[i - 1] == begin:
                result += ',%d' % time_list[i - 1]
            else:
                result += ',%d-%d' % (begin, time_list[i - 1])
            begin = time_list[i]
    return result[1:] + '/全周'


def read_lesson(lesson_str):
    """
    将节次信息分裂为适当的片段
    解决半节课，多节课连续的问题
    :param lesson_str: 教务的节次信息
    :return: 经过解析后的节次信息数据
    """
    # 课程连续过多，例如：1010203
    if len(lesson_str) == 0:
        raise util.ErrorSignal('课程信息为空:{}'.format(lesson_str))
    if len(lesson_str) != 5:
        day = lesson_str[0]
        lesson = []
        for i in range(1, len(lesson_str), 4):
            num = lesson_str[i] + lesson_str[i + 1]
            num = int(num)
            num += num % 2
            lesson.append('%s%02d%02d' % (day, num - 1, num))
        return lesson
    return [lesson_str]


def next_lesson(lesson_str):
    """
    解析出该课程的下一节课
    为多节课连接的情况提供服务
    :param lesson_str: 当前课程的节次（必须为标准格式）
    :return: 下一节课的节次
    """
    day = lesson_str[0]
    time1 = int(lesson_str[1:2])
    time2 = int(lesson_str[3:4])
    next_lesson_str = '%s%02d%02d' % (day, time1 - 1, time2)
    return next_lesson_str


def sbc2dbc(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif 65281 <= inside_code <= 65374:  # 全角字符（除空格）根据关系转化
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring


def dbc2sbc(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif 32 <= inside_code <= 126:  # 半角字符（除空格）根据关系转化
            inside_code += 65248
        rstring += chr(inside_code)
    return rstring
