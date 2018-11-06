# -*- coding: utf-8 -*-
# Common package
# Personal package
import util


def room_all(data_set):
    """
    单线程处理函数
    完成对所有教室数据的校验
    :param data_set: 所有教室的数据
    :return: 经过过滤的数据
    """
    result = []
    for room in data_set:
        if 'name' not in room or 'building' not in room or 'campus' not in room:
            raise util.ErrorSignal('课程{}缺少字段'.format(room))
        room['name'] = room['name'].strip()
        room['campus'] = room['campus'].strip()
        room['building'] = room['building'].strip()
        if room not in result:
            result.append(room)
    return result


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


def read_hour(hour_str):
    """
    将学生课表上的课时信息提取出来
    :param hour_str: 课时信息字符串
    :return: 经过解析后的课时信息数据
    """
