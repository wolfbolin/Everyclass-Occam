# -*- coding: utf-8 -*-
# Common package
import os
import json
# Personal package
import util
import spider
import filter
import database


def build_folder(semester):
    """
    在进行写入之前检查文件夹存在状态
    cache
    |--semester\
    |  |--teacher_xml\
    |  |--student_xml\
    |  |--student_json\
    |--global\
    |  |--student
    |  |--teacher
    |--log\
    |--output\
    :param semester: 学期数据
    """
    util.print_a('开始初始化本地缓存')
    paths = [
        './cache/%s/' % semester,
        './cache/%s/teacher_html/' % semester,
        './cache/%s/teacher_json/' % semester,
        './cache/%s/student_html/' % semester,
        './cache/%s/student_json/' % semester,
        './cache/global/',
        './cache/output/',
        './cache/log/'
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
    util.print_d('本地缓存初始化完毕')


def build_table(semester):
    """
    在数据写入之前清空或建立数据表
    :param semester: 学期数据
    :return: rowcount
    """
    util.print_a('开始初始化数据表')
    conn = database.connect()
    database.remove_tables(conn, semester)
    database.add_tables(conn, semester)
    database.add_foreign(conn, semester)
    util.print_d('数据表初始化完毕')


def build_room():
    """
    全盘考虑教室数据获取与写入
    :return: rowcount
    """
    util.print_a('开始处理所有教室的数据')
    rowcount = 0
    cookie = spider.cookie()

    util.print_t('Step1:正在获取所有教室的数据')
    if util.query_from_cache('global', '', 'all_room'):
        all_room = util.read_from_cache('global', '', 'all_room')
        all_room = json.loads(all_room)
        util.print_d('已从缓存中读取数据')
    else:
        all_room = spider.all_room(cookie)
        util.save_to_cache('global', '', 'all_room', json.dumps(all_room))
        util.print_d('已从网络获取数据并缓存')

    # 数据过滤代码片段
    util.print_t('Step2:正在校验所有教室的数据')
    all_room = filter.all_room(all_room)

    # 向数据库中写入数据
    util.print_t('Step3:正在写入所有教室的数据')
    conn = database.connect()
    database.clean_table(conn, 'all_room')
    rowcount += database.room_update(all_room, conn)

    util.print_d('所有教室的数据已处理完毕')
    return rowcount


