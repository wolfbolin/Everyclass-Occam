# -*- coding: utf-8 -*-
# Common package
import time
import json
from math import ceil
# Personal package
import util
import database


def correct_error_data_all():
    """

    :return:
    """
    util.print_a('开始修正偏移数据')
    rowcount = 0

    # 检索数据库中已有的学期
    mysql_conn = database.mysql_connect()
    semester_list = database.get_semester_list(mysql_conn)
    mysql_conn.close()

    # 逐学期修正数据
    for index, semester in enumerate(semester_list):
        util.print_w('Step1.{}:更新{}学期的修正数据偏移'.format(index + 1, semester))
        sql_count = correct_error_data(semester)
        rowcount += sql_count


def correct_error_data(semester):
    """
    修正数据库中的异常数据
    :param semester:
    :return: rowcount
    """
    util.print_a('开始处理所有异常的数据')
    mysql_conn = database.mysql_connect()
    rowcount = 0

    util.print_t('Step1:正在处理教室相关数据异常')
    time_start = time.time()

    util.print_i('Step1.1:正在获取教室异常数据')
    # 获取源数据
    error_room_list = database.error_room_select(mysql_conn, semester)
    if len(error_room_list) > 0:
        util.print_i('Step1.2:正在获取教室源数据')
        room_list = database.room_select(mysql_conn, semester)

        util.print_i('Step1.3:正在纠正教室异常数据')
        room_index = {}
        for room in room_list:
            room_index[room['name']] = room
        change_log = []
        for error_room in error_room_list:
            if error_room['room'] in room_index:
                new_room = room_index[error_room['room']]
                util.print_w('教室%s将%s重置为%s'
                             % (error_room['room'], error_room['roomID'], new_room['code']))
                change_log.append({
                    'semester': semester,
                    'type': '无效的教室信息映射',
                    'old': error_room['roomID'],
                    'new': new_room['code']
                })
                error_room['roomID'] = new_room['code']
            else:
                util.print_w('教室%s无法在数据库中找到，已置为空教室' % error_room['room'])
                change_log.append({
                    'semester': semester,
                    'type': '无效的教室信息映射',
                    'old': error_room['roomID'],
                    'new': ''
                })
                error_room['roomID'] = ''
        # 保持修改日志
        util.save_to_log('chang_log_%s_card_error_room' % semester, json.dumps(change_log))
        # 交给数据库完成修改
        sql_count = database.error_room_update(mysql_conn, semester, error_room_list)
        # 完成修改，反馈结果
        time_end = time.time()
        util.print_d('%s学期的教室数据异常修正完毕，耗时%d秒，操作数据库%d行' % (semester, ceil(time_end - time_start), sql_count))
        rowcount += sql_count
    else:
        util.print_i('Step1.2:该学期教室数据无需修正')

    return rowcount
