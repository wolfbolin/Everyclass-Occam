# -*- coding: utf-8 -*-
# Common package
import re
import json
from hashlib import md5
from bs4 import BeautifulSoup
# Personal package
import util


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
        student_data = util.read_from_cache(semester, 'student_json', student_code)
        student_data = json.loads(student_data)
    elif util.query_from_cache(semester, 'student_html', student_code):
        student_html = util.read_from_cache(semester, 'student_html', student_code)
        student_data = student_table_analysis(student_html, semester, student_name, student_code)
        util.save_to_cache(semester, 'student_json', student_code, json.dumps(student_data))
    else:
        raise util.ErrorSignal('缺少学生%s课表数据' % student_code)

    # Fix Bug 2018-12-17 --Begin
    klass_id_index = {}  # 创建节次数据索引
    # Fix Bug 2018-12-17 --end

    for index, card in enumerate(student_data):
        for key in card:
            if isinstance(card[key], str):
                card[key] = card[key].replace('\xa0', '').replace('\u3000', '').strip()

        card['teacher'] = card['teacher_string']
        card['week_list'] = util.read_week(card['week_string'])
        card['week'] = card['week_list']
        card['room'] = util.sbc2dbc(card['room'])
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
                student_data[pair[1]]['klassID'] += '&%d' % index
    # Fix Bug 2018-12-17 --end

    # 将结果添加到结果集中
    result = [{
        'student_name': student_name,
        'student_code': student_code,
        'table': student_data
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
                    card['klassID'] = re.findall('jx0408id=(.*?)&', course['onclick'], re.S | re.M)[0]
                    card['roomID'] = re.findall('classroomID=(.*?)&', course['onclick'], re.S | re.M)[0]
                    card['name'] = course_names[index].find('font').string
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
