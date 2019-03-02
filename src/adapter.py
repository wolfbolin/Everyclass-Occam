# -*- coding: utf-8 -*-
# Common package
import pymysql
from warnings import filterwarnings
# Personal package
import builder
import filter
import util

# 将数据库警告定义为错误方便捕获
filterwarnings('error', category=pymysql.Warning)

if __name__ == "__main__":
    # 完成所有学期搜索信息的更新
    document = input("更新所有学期搜索数据库(y/n)：")
    if document is 'y':
        builder.build_search_all()
        exit()

    # 设置运行的学期信息
    semester = input("请输入需要更新的学期：")
    if filter.check_semester(semester) is not True:
        util.print_e('输入的学期信息错误，请检查您的输入')
        exit()

    document = input("仅更新本学期搜索数据库(y/n)：")
    if document is 'y':
        # 完成该学期搜索信息的更新
        builder.build_search_semester(semester=semester)
        exit()

    # 创建本地缓存文件夹
    builder.build_folder(semester=semester)

    # 创建本学期数据表
    builder.build_table(semester=semester)

    # 刷新所有教室的信息
    builder.build_room()

    # 刷新所有教师的信息
    builder.build_teacher()

    # 刷新所有学生的信息
    builder.build_student()

    # 获取本学期教师的课程表
    builder.build_teacher_table(semester=semester)

    # 获取本学期学生的课程表
    builder.build_student_table(semester=semester)

    # 完成该学期搜索信息的更新
    builder.build_search_semester(semester=semester)
