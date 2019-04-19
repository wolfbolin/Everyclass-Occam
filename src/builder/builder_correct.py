# -*- coding: utf-8 -*-
# Common package
import time
import json
from math import ceil
# Personal package
import util
import filter
import database


def save_change_log(semester, change_log):
    """
    写入本次做出修改的数据
    """
    util.print_a('正在保存该学期修改日志')
    rowcount = 0
    if len(change_log) == 0:
        # 无修改，不记录
        return 0
    # 连接到数据库
    mongo_conn = database.mongo_connect(util.mongo_entity_database)
    # 删除旧的修改日志
    sql_count = database.change_log_delete(mongo_conn, semester)
    rowcount += sql_count
    # 写入新的修改日志
    sql_count = database.change_log_insert(mongo_conn, change_log)
    rowcount += sql_count

    return rowcount


def correct_room_data(semester):
    """
    修正数据库中的异常数据
    :return: rowcount
    """
    util.print_a('正在修正该学期错误的教室数据')

    util.print_t('Step1:正在处理教室相关数据异常')
    mysql_conn = database.mysql_connect(util.mysql_entity_database)
    rowcount = 0
    time_start = time.time()

    util.print_i('Step1.1:正在获取教室异常数据')
    # 检查异常数据
    error_room_list = database.error_room_select(mysql_conn, semester)
    if len(error_room_list) > 0:
        util.print_i('Step1.2:正在获取教室源数据')
        room_list = database.room_select(mysql_conn, 'room')

        util.print_i('Step1.3:正在纠正教室异常数据')
        # 纠正教室异常数据
        error_room_list, change_log = filter.error_room(semester, error_room_list, room_list)

        util.print_i('Step1.4:正在写入修正数据')
        # 交给数据库完成修改
        sql_count = database.error_room_update(mysql_conn, semester, error_room_list)
        # 完成修改，反馈结果
        time_end = time.time()
        util.print_d('%s学期的教室数据异常修正完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
        rowcount += sql_count
    else:
        util.print_i('Step1.2:该学期教室数据无需修正')
        change_log = []

    return rowcount, change_log


def correct_klass_data(semester):
    """
    修正数据库中的异常数据
    :return: rowcount
    """
    util.print_a('正在修正该学期错误的课程数据')

    util.print_t('Step1:正在处理重复课程异常')
    mysql_conn = database.mysql_connect(util.mysql_entity_database)
    rowcount = 0
    time_start = time.time()

    util.print_i('Step1.1:正在获取课程号异常数据')
    # 检测异常数据
    doubt_klass_list = database.doubt_klass_list(mysql_conn, semester)
    if len(doubt_klass_list) > 0:
        util.print_i('Step1.2:正在获取重复的课程映射信息')
        klass_map_list = database.klass_map_list(mysql_conn, semester, doubt_klass_list)
        util.save_to_output('klass_map_list', json.dumps(klass_map_list))

        util.print_i('Step1.3:正在纠正课程号异常数据')
        # 纠正课程号异常数据
        error_klass_list, change_log = filter.error_klass(semester, klass_map_list)

        util.print_i('Step1.4:正在写入修正数据')
        # 交给数据库完成修改
        sql_count = database.error_class_update(mysql_conn, semester, error_klass_list)
        # 完成修改，反馈结果
        time_end = time.time()
        util.print_d('%s学期的教室数据异常修正完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
        rowcount += sql_count
    else:
        util.print_i('Step1.2:该学期课程数据无需修正')
        change_log = []

    return rowcount, change_log
