# -*- coding: utf-8 -*-
# Common package
import re
import time
from math import ceil
# Personal package
import util
import database


def build_search_semester(semester):
    """
    清除所有角色本学期的检索信息并全部重新添加
    :param semester: 需要重建的学期
    :return: rowcount
    """
    util.print_a('开始重建该学期搜索文档库')
    rowcount = 0

    util.print_t('Step1:正在处理学生搜索文档数据')

    util.print_i('Step1.1:正在删除该学期的旧数据')
    mongo_conn = database.mongo_connect(util.mongo_entity_database)
    sql_count = database.search_semester_delete(mongo_conn, 'search', semester)
    rowcount += sql_count

    util.print_t('Step2:正在写入搜索文档数据')

    util.print_i('Step2.1:正在写入新的学生数据')
    time_start = time.time()
    mysql_conn = database.mysql_connect(util.mysql_entity_database)  # 建立MySQL连接
    student_list = database.entity_student_select(mysql_conn, semester)  # 查询学生信息
    mysql_conn.close()  # 关闭数据库连接
    sql_count = util.multiprocess(task=database.search_update, main_data=student_list, max_thread=10,
                                  multithread=util.mongo_multithread,
                                  attach_data={
                                      'semester': semester,
                                      'type': 'student',
                                      'conversion': ['deputy', 'klass']
                                  })
    time_end = time.time()
    util.print_d('%s学期的学生文档数据更新完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
    rowcount += sql_count

    util.print_i('Step2.2:正在写入新的教师数据')
    time_start = time.time()
    mysql_conn = database.mysql_connect(util.mysql_entity_database)  # 建立MySQL连接
    teacher_list = database.entity_teacher_select(mysql_conn, semester)  # 查询教师信息
    mysql_conn.close()
    sql_count = util.multiprocess(task=database.search_update, main_data=teacher_list, max_thread=10,
                                  multithread=util.mongo_multithread,
                                  attach_data={
                                      'semester': semester,
                                      'type': 'teacher',
                                      'conversion': ['unit', 'title']
                                  })
    time_end = time.time()
    util.print_d('%s学期的教师文档数据更新完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
    rowcount += sql_count

    return rowcount
