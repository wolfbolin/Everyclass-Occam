# -*- coding: utf-8 -*-
# Common package
import re
import json
from hashlib import md5
from bs4 import BeautifulSoup
# Personal package
import util


def teacher_all(data_set):
    """
    单线程处理函数
    完成对所有教师的信息的数据校验
    :param data_set: 所有教师的数据
    :return: 经过过滤的数据
    """
    teacher_template = util.teacher_info.copy()
    for teacher in data_set:
        for key in teacher_template:
            try:
                teacher[key] = teacher[key].replace('\xa0', '').replace('\u3000', '').strip()
            except TypeError as e:
                raise util.ErrorSignal('教师{}缺少字段'.format(teacher))
        teacher['code'] = teacher['code'].replace('*', '#')
        teacher['name'] = teacher['name'].replace('*', '#')
    return data_set


def teacher_list(data_set):
    """
    单线程函数
    完成对教师名单的数据校验
    :param data_set: 所有教师的数据
    :return: 经过过滤的数据
    """
    for teacher in data_set:
        try:
            teacher['jg0101id'] = teacher['jg0101id'].replace('\xa0', '').replace('\u3000', '').strip()
            teacher['jgh'] = teacher['jgh'].replace('\xa0', '').replace('\u3000', '').strip()
            teacher['xm'] = teacher['xm'].replace('\xa0', '').replace('\u3000', '').strip()
            teacher['jgh'] = teacher['jgh'].replace('*', '#')
            teacher['xm'] = teacher['xm'].replace('*', '#')
            teacher['teacher_code'] = teacher['jgh']
            teacher['teacher_name'] = teacher['xm']
        except TypeError as e:
            raise util.ErrorSignal('教师{}缺少字段'.format(teacher))
    return data_set


def teacher_table(data_set):
    """
    多线程函数
    完成对教师课表的校验与整合
    :param data_set: 学期 20xx-20xx-x + 所有教师的数据
    :return: 经过过滤的数据
    """
    semester = data_set['semester']
    teacher_name = data_set['teacher_name']
    teacher_code = data_set['teacher_code']
    if util.query_from_cache(semester, 'teacher_json', teacher_code):
        teacher_json = util.read_from_cache(semester, 'teacher_json', teacher_code)
        teacher_json = json.loads(teacher_json)
    elif util.query_from_cache(semester, 'teacher_html', teacher_code):
        teacher_html = util.read_from_cache(semester, 'teacher_html', teacher_code)
        teacher_json = teacher_table_analysis(teacher_html, semester, teacher_name, teacher_code)
        util.save_to_cache(semester, 'teacher_json', teacher_code, json.dumps(teacher_json))
    else:
        raise util.ErrorSignal('缺少教师%s课表数据' % teacher_code)

    for card in teacher_json:
        for key in card:
            if isinstance(card[key], str):
                card[key] = card[key].replace('\xa0', '').replace('\u3000', '').strip()

        card['teacher'] = card['teacher_string']
        card['week_list'] = util.read_week(card['week_string'])
        card['week'] = card['week_list']
        # md5_str = '/'.join([';'.join(card['week']), card['lesson'], card['room'], card['course_name']])
        # md5_str = md5_str.encode('utf-8')
        # md5_code = md5(md5_str).hexdigest()
        # card['md5'] = md5_code
        card['room'] = util.sbc2dbc(card['room'])
        card['pick'] = int(card['pick'].replace('人', ''))
        card['hour'] = int(card['hour'])

    # 将结果添加到结果集中
    result = [{
        'teacher_name': teacher_name,
        'teacher_code': teacher_code,
        'table': teacher_json
    }]
    return result


def teacher_table_analysis(html, semester, teacher_name, teacher_code):
    """
    单线程函数
    根据下载的文件分析教师的课程表
    :param html: 原始数据
    :param semester: 课表学期
    :param teacher_name: 教师基础信息
    :param teacher_code: 教师基础信息
    :return: 经过格式化的数据
    """
    result = []
    soup = BeautifulSoup(html, 'lxml')
    lines = soup.find('table').find_all('tr')
    for line_index, line in enumerate(lines[1:6]):
        columns = line.find_all('td')
        for column_index, column in enumerate(columns[1:]):
            courses = column.find(class_='kbcontent').find_all('a')
            if len(courses) == 0:
                continue
            # 此处需要确定课程在表格中的位置
            # line_index映射0102，0304，0506，0708，0910，1112
            # column_index映射1，2，3，4，5，6，7
            lesson = str(column_index + 1)
            lesson += str(line_index * 2 + 1).zfill(2)
            lesson += str((line_index + 1) * 2).zfill(2)
            for course in courses:
                card = util.card_info.copy()
                try:
                    card['klassID'] = re.findall('jx0408id=(.*?)&', course['onclick'], re.S | re.M)[0]
                    card['roomID'] = re.findall('classroomID=(.*?)&', course['onclick'], re.S | re.M)[0]
                    card['teacher_string'] = teacher_name
                    card['lesson'] = lesson
                    if course.find(title='课程名称') is not None:
                        card['name'] = course.find(title='课程名称').string
                    if course.find(title='周次') is not None:
                        card['week_string'] = course.find(title='周次').string
                    if course.find(title='单双周') is not None:
                        card['week_string'] += '/' + course.find(title='单双周').string
                    if course.find(title='上课地点教室') is not None:
                        card['room'] = course.find(title='上课地点教室').string
                    # 以下内容为附加内容
                    if course.find(title='选课人数') is not None:
                        card['pick'] = course.find(title='选课人数').string
                    if course.find(title='教学班名称') is not None:
                        if len(list(course.find(title='教学班名称').strings)) > 0:
                            card['klass'] = list(course.find(title='教学班名称').strings)[0]
                    if course.find(title='上课总学时') is not None:
                        card['hour'] = course.find(title='上课总学时').string
                    if course.find(title='课程性质') is not None:
                        card['type'] = course.find(title='课程性质').string
                except (AttributeError, IndexError) as e:
                    raise util.ErrorSignal('教师%s课表解析错误，%s' % (teacher_name + teacher_code, e))
                result.append(card)

    # 分析结束，返回结果
    return result
