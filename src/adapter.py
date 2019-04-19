# -*- coding: utf-8 -*-
# Common package
import pymysql
from warnings import filterwarnings
# Personal package
import database
import builder
import filter
import util

# 将数据库警告定义为错误方便捕获
filterwarnings('error', category=pymysql.Warning)

if __name__ == "__main__":
    document = input("更新所有学期or某一学期的课程数据(y/20xx-20xx-x/other)：")
    semester_list = []
    if document == 'y':
        # 检索数据库中已有的学期
        mysql_conn = database.mysql_connect(util.mysql_occam_database)
        semester_list = database.get_semester_list(mysql_conn)
        mysql_conn.close()

        # 刷新所有教师的信息
        builder.build_teacher()

        # 刷新所有学生的信息
        builder.build_student()

        # 刷新所有教室的信息
        builder.build_room()

    elif filter.check_semester(document) is True:
        semester_list = document
    else:
        util.print_e('请做出正确的选择')
        exit()

    for semester in semester_list:
        util.print_w('正在更新%s学期的课程数据' % semester)

        # 创建本地缓存文件夹
        builder.build_folder(semester=semester)

        # 创建本学期数据表
        builder.build_table(semester=semester)

        # 获取本学期教师的课程表
        builder.build_teacher_table(semester=semester)

        # 获取本学期学生的课程表
        builder.build_student_table(semester=semester)
