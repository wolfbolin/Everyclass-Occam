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
    'code': '',
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
    'name': '',
    'teacher_string': '',  # 教师信息的原始数据
    'teacher_list': [],  # 教师信息的解析形式
    'teacher': '',  # 教师信息的合成数据
    'week_string': '',  # 周次信息的原始数据
    'week_list': [],  # 周次信息的解析形式
    'week': '',  # 周次信息的合成数据
    'lesson': '',
    'room': '',
    'klass': '',
    # 以下内容为老师课表附加内容
    'pick': 0,
    'hour': 0,
    'type': '',
    # 系统隐藏ID
    'klassID': '',
    'roomID': ''
}
