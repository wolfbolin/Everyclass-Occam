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
        teacher_data = util.read_from_cache(semester, 'teacher_json', teacher_code)
        teacher_data = json.loads(teacher_data)
    elif util.query_from_cache(semester, 'teacher_html', teacher_code):
        teacher_html = util.read_from_cache(semester, 'teacher_html', teacher_code)
        teacher_data = teacher_table_analysis(teacher_html, semester, teacher_name, teacher_code)
        util.save_to_cache(semester, 'teacher_json', teacher_code, json.dumps(teacher_data))
    else:
        raise util.ErrorSignal('缺少教师%s课表数据' % teacher_code)

    # Fix Bug 2018-12-17 --Begin
    klass_id_index = {}  # 创建节次数据索引
    # Fix Bug 2018-12-17 --end

    for index, card in enumerate(teacher_data):
        for key in card:
            if isinstance(card[key], str):
                card[key] = card[key].replace('\xa0', '').replace('\u3000', '').strip()

        card['teacher'] = card['teacher_string']
        card['week_list'] = util.read_week(card['week_string'])
        card['week'] = card['week_list']
        card['room'] = util.sbc2dbc(card['room'])
        card['pick'] = int(card['pick'].replace('人', ''))
        card['hour'] = int(card['hour'])

        # Fix Bug 2018-12-17 --Begin
        if card['klassID'] in klass_id_index:
            klass_id_index[card['klassID']].append((card['lesson'], index))
        else:
            klass_id_index[card['klassID']] = [(card['lesson'], index)]
        # Fix Bug 2018-12-17 --end

    """
    Fix Bug 2018-12-17
    通过对于每节课向后搜索的模式，确定每节课是不是多节课连接的状态
    对于多节课连接的课程，将当前的课程名进行重命名，以避免重复的klassID造成重复
    当课程ID重复时，按照lesson进行排序，并且从前到后向klassID中添加数字后缀予以区分
    该方案假设前提，klassID相同的课程，lesson都是不同的
    klassID_index = {
        'klassID1': [ ('lesson': index), ... ],
        'klassID2': ...
    }
    """
    for klassID in klass_id_index:  # 读取相同的klassID数据集合
        if len(klass_id_index[klassID]):  # 说明课程ID不唯一
            sorted(klass_id_index[klassID])  # 按照课程节次对课程进行排序
            for index, pair in enumerate(klass_id_index[klassID]):
                # 使用数据集合中记录的数组下标更新课程ID
                teacher_data[pair[1]]['klassID'] += '%d' % index
    # Fix Bug 2018-12-17 --end

    # 将结果添加到结果集中
    result = [{
        'teacher_name': teacher_name,
        'teacher_code': teacher_code,
        'table': teacher_data
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
