# -*- coding: utf-8 -*-
# Common package
# Personal package
import util


def course_all(data_set):
    """
    单线程处理函数
    完成对所有学生的信息的数据校验
    :param data_set: 所有学生的数据
    :return: 经过过滤的数据
    """
    course_template = util.course_info.copy()
    for course in data_set:
        for key in course_template:
            try:
                course[key] = course[key].replace('\xa0', '').replace('\u3000', '').strip()
            except TypeError as e:
                raise util.ErrorSignal('课程{}缺少字段'.format(course))
    return data_set


def course_list(data_set, course_info):
    """
    单线程处理函数
    完成对课程相关信息的数据校验
    :param data_set: 所有课程信息
    :param course_info: 所有课程的数据
    :return: rowcount
    """
    course_set = {}
    for course in course_info:
        course_set[course['name']] = course
    for course in data_set:
        try:
            course['jx02id'] = course['jx02id'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            course['kcmc'] = course['kcmc'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            course['kch'] = course['kch'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            course['code'] = course['kch']
            course['name'] = course['kcmc']
            course['credit'] = int(float(course_set[course['name']]['credit'])*10)
        except TypeError as e:
            raise util.ErrorSignal('课程{}缺少字段'.format(course))
    return data_set

