# -*- coding: utf-8 -*-
# Common package
import re
import time
from math import ceil
# Personal package
import util
import database


def build_search_all():
    """
    清除所有角色的检索信息并全部重新添加
    :return: rowcount
    """
    util.print_a('开始重建搜索文档库')
    rowcount = 0

    # 检索数据库中已有的学期
    mysql_conn = database.mysql_connect()
    semester_list = database.get_semester_list(mysql_conn)
    mysql_conn.close()

    util.print_t('Step1:正在处理学生文档数据')

    util.print_i('Step1.1:正在删除旧的数据')
    mongo_conn = database.mongo_connect()
    sql_count = database.clean_document(mongo_conn, 'student')
    rowcount += sql_count

    util.print_i('Step1.2:正在写入新的数据')
    for semester in semester_list:
        util.print_i('更新%s学期的学生文档数据' % semester)
        time_start = time.time()
        mysql_conn = database.mysql_connect()  # 建立MySQL连接
        student_list = database.student_select(mysql_conn, semester)  # 查询学生信息
        mysql_conn.close()
        sql_count = util.multiprocess(task=database.student_update_search, main_data=student_list, max_thread=10,
                                      multithread=util.mongo_multithread, attach_data={'semester': semester})
        time_end = time.time()
        util.print_d('%s学期的学生文档数据更新完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
        rowcount += sql_count

    util.print_t('Step2:正在处理学生文档数据')

    util.print_i('Step2.1:正在删除旧的数据')
    mongo_conn = database.mongo_connect()
    sql_count = database.clean_document(mongo_conn, 'teacher')
    rowcount += sql_count

    util.print_i('Step2.2:正在写入新的数据')
    for semester in semester_list:
        util.print_i('更新%s学期的教师文档数据' % semester)
        time_start = time.time()
        mysql_conn = database.mysql_connect()  # 建立MySQL连接
        teacher_list = database.teacher_select(mysql_conn, semester)  # 查询教师信息
        mysql_conn.close()
        sql_count = util.multiprocess(task=database.teacher_update_search, main_data=teacher_list, max_thread=10,
                                      multithread=util.mongo_multithread, attach_data={'semester': semester})
        time_end = time.time()
        util.print_d('%s学期的教师文档数据更新完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
        rowcount += sql_count
