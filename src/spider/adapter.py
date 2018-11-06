# -*- coding: utf-8 -*-
# Common package
import pymysql
from warnings import filterwarnings
# Personal package
import builder

# 运行相关的配置设置
# 将数据库警告定义为错误方便捕获
filterwarnings('error', category=pymysql.Warning)
# 重建学生与教师的数据总表（警告：该操作将清空数据库）
rebuild_base_table = False
# 设置运行的学期
semester = '2017-2018-1'
# 线程数不可提前设计，需要根据数据量进行调教

if __name__ == "__main__":
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
