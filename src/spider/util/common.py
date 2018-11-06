# -*- coding: utf-8 -*-
"""
该文件内包含大部分需要预定义的数据结构
不包含可用的函数与类定义
"""

# 数据库部分预定义数据
table_name_template = [
    # 数组顺序需保持该顺序，方便删除表
    'student_link_{}',
    'teacher_link_{}',
    'teacher_{}',
    'student_{}',
    'card_{}',
]

# 教室数据结构
room_info = {
    'name': '',
    'building': '',
    'campus': ''
}

# 教师的个人信息数据结构
teacher_info = {
    'code': '',
    'name': '',
    'unit': '',
    'title': '',
    'qualification': ''
}

# 学生的个人信息数据结构
student_info = {
    'code': '',
    'name': '',
    'klass': '',
    'deputy': '',
    'campus': ''
}

# 课程卡片信息数据结构
card_info = {
    # 课程卡片信息
    'course_name': '',
    'teacher_string': '',
    'teacher_list': [],
    'teacher': '',
    'week_string': '',
    'week_list': [],
    'week': '',
    'lesson': '',
    'room': '',
    'md5': '',
    # 以下内容为老师课表附加内容
    'pick': 0,
    'code': '',
    'hour': 0,
    'type': '',
    # 系统隐藏ID
    'jx0408id': '',
    'classroomID': ''
}
