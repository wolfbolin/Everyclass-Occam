# -*- coding: utf-8 -*-
# Common package
import re
import json
from hashlib import md5
from bs4 import BeautifulSoup
# Personal package
import util
from .filter_base import read_week, make_week


def student_all(data_set):
    """
    单线程处理函数
    完成对所有学生的信息的数据校验
    :param data_set: 所有学生的数据
    :return: 经过过滤的数据
    """
    student_template = util.student_info.copy()
    for student in data_set:
        for key in student_template:
            try:
                student[key] = student[key].replace('\xa0', '').replace('\u3000', '').strip()
            except TypeError as e:
                raise util.ErrorSignal('学生{}缺少字段'.format(student))
    return data_set


def student_list(data_set):
    """
    单线程处理函数
    完成对上课学生名单数据的范化
    :param data_set: 上课学生名单
    :return: 经过过滤的数据
    """
    for student in data_set:
        try:
            student['xs0101id'] = student['xs0101id'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            student['xm'] = student['xm'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            student['xh'] = student['xh'].strip().replace('\xa0', '').replace('\u3000', '')  # 过滤不可见字符
            student['student_code'] = student['xh']
            student['student_name'] = student['xm']
        except TypeError as e:
            raise util.ErrorSignal('学生{}缺少字段'.format(student))
    return data_set


def student_table(data_set):
    """
    多线程函数
    完成对学生课表的校验与整合
    :param data_set: 学期 20xx-20xx-x + 所有教师的数据
    :return: 经过过滤的数据
    """
    semester = data_set['semester']
    student_name = data_set['student_name']
    student_code = data_set['student_code']
    if util.query_from_cache(semester, 'student_json', student_code):
        student_json = util.read_from_cache(semester, 'student_json', student_code)
        student_json = json.loads(student_json)
    elif util.query_from_cache(semester, 'student_html', student_code):
        student_html = util.read_from_cache(semester, 'student_html', student_code)
        student_json = student_table_analysis(student_html, semester, student_name, student_code)
        util.save_to_cache(semester, 'student_json', student_code, json.dumps(student_json))
    else:
        raise util.ErrorSignal('缺少学生%s课表数据' % student_code)

    for card in student_json:
        for key in card:
            if isinstance(card[key], str):
                card[key] = card[key].replace('\xa0', '').replace('\u3000', '').strip()

        card['teacher'] = card['teacher_string']
        card['week_list'] = read_week(card['week_string'])
        card['week'] = make_week(card['week_list'])
        md5_str = '/'.join([';'.join(card['week']), card['lesson'], card['room'], card['course_name']])
        md5_str = md5_str.encode('utf-8')
        md5_code = md5(md5_str).hexdigest()
        card['md5'] = md5_code
        card['hour'] = int(card['hour'])

    # 将结果添加到结果集中
    result = [{
        'student_name': student_name,
        'student_code': student_code,
        'table': student_json
    }]
    return result


def student_table_analysis(html, semester, student_name, student_code):
    """
    多线程处理函数
    根据下载的文件分析学生的课程表
    :param html: 原始数据
    :param semester: 课表学期
    :param student_name: 学习基础信息
    :param student_code: 学习基础信息
    :return: 经过过滤的数据
    """
    result = []
    soup = BeautifulSoup(html, 'lxml')
    try:
        lines = soup.find('table').find_all('tr')
    except AttributeError as e:
        util.del_from_cache(semester, 'student_html', student_code)
        util.print_e("存在无法读取学生%s，已删除。%s" % (student_name + student_code, e))
        return result
    for line_index, line in enumerate(lines[1:6]):  # 第一行为表头，最后一行为备注
        columns = line.find_all('td')
        for column_index, column in enumerate(columns[1:]):  # 第一列为时间段
            try:
                courses = column.find(class_='kbcontent').find_all('a')
                if len(courses) == 0:
                    continue
                course_names = column.find(class_='kbcontent1').find_all('a')
                course_hour = column.find_all(class_='kbcontent')[2].string
                course_hours = re.findall(':([0-9]*?)\)', course_hour, re.S | re.M)
            except BaseException as e:
                util.del_from_cache(semester, 'student_html', student_code)
                util.print_e("存在无法读取学生%s，已删除。%s" % (student_name + student_code, e))
                return result
            # 此处需要确定课程在表格中的位置
            # line_index映射0102，0304，0506，0708，0910，1112
            # column_index映射1，2，3，4，5，6，7
            lesson = str(column_index + 1)
            lesson += str(line_index * 2 + 1).zfill(2)
            lesson += str((line_index + 1) * 2).zfill(2)
            for index, course in enumerate(courses):
                card = util.card_info.copy()
                try:
                    card['jx0408id'] = re.findall('jx0408id=(.*?)&', course['onclick'], re.S | re.M)[0]
                    card['classroomID'] = re.findall('classroomID=(.*?)&', course['onclick'], re.S | re.M)[0]
                    card['course_name'] = course_names[index].find('font').string
                    card['lesson'] = lesson
                    if course.find(title='老师') is not None:
                        card['teacher_string'] = course.find(title='老师').string
                    if course.find(title='周次') is not None:
                        card['week_string'] = course.find(title='周次').string
                    if course.find(title='单双周') is not None:
                        card['week_string'] += '/' + course.find(title='单双周').string
                    if course.find(title='上课地点教室') is not None:
                        card['room'] = course.find(title='上课地点教室').string
                    if len(course_hours) == len(course):  # 课时信息
                        card['hour'] = course_hours[index]
                except (AttributeError, IndexError) as e:
                    raise util.ErrorSignal('学生%s课表解析错误，%s' % (student_name + student_code, e))
                result.append(card)

    # 分析结束，返回结果
    return result
