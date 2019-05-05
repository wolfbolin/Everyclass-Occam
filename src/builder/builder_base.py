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


def build_occam_table(semester):
    """
    在数据写入之前清空或建立数据表
    :param semester: 学期数据
    :return: rowcount
    """
    util.print_a('开始初始化数据表')
    conn = database.mysql_connect(util.mysql_occam_database)
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
    if util.query_from_cache('global', '', 'room_all'):
        room_all = util.read_from_cache('global', '', 'room_all')
        room_all = json.loads(room_all)
        util.print_d('已从缓存中读取数据')
    else:
        room_all = spider.room_all(cookie)
        util.save_to_cache('global', '', 'room_all', json.dumps(room_all))
        util.print_d('已从网络获取数据并缓存')

    # 数据过滤代码片段
    util.print_t('Step2:正在校验所有教室的数据')
    room_all = filter.room_all(room_all)

    # 向数据库中写入数据
    util.print_t('Step3:正在写入所有教室的数据')
    conn = database.mysql_connect(util.mysql_occam_database)
    rowcount += database.room_update(conn, 'room_all', room_all)

    util.print_d('所有教室的数据已处理完毕')
    return rowcount


def build_entity_table():
    """
    清空Entity数据库中与课程相关的所有数据
    :return: rowcount
    """
    util.print_w('清空Entity数据库中所有课程数据')
    rowcount = 0
    entity_conn = database.mysql_connect(util.mysql_entity_database)
    rowcount += database.clean_table(entity_conn, 'student_link')
    rowcount += database.clean_table(entity_conn, 'teacher_link')
    rowcount += database.clean_table(entity_conn, 'student')
    rowcount += database.clean_table(entity_conn, 'teacher')
    rowcount += database.clean_table(entity_conn, 'card')
    rowcount += database.clean_table(entity_conn, 'room')
    return rowcount


def copy_mysql_data(semester):
    """
    将该学期的数据复制到线上服务数据中
    :param semester: 需要聚合的学期
    :return: rowcount
    """
    util.print_a('开始拷贝%s学期所有数据' % semester)
    rowcount = 0
    occam_conn = database.mysql_connect(util.mysql_occam_database)
    entity_conn = database.mysql_connect(util.mysql_entity_database)

    util.print_t('Step1:正在拷贝教师数据')

    util.print_i('Step1.1:正在读取新的教师数据')
    teacher_list = database.teacher_select(occam_conn, 'teacher_%s' % semester)
    util.print_i('Step1.2:正在写入新的教师数据')
    rowcount += util.multiprocess(task=database.entity_teacher_insert, main_data=teacher_list, max_thread=30,
                                  attach_data={'semester': semester, 'mysql_database': util.mysql_entity_database},
                                  multithread=util.mysql_multithread)

    util.print_t('Step2:正在拷贝学生数据')

    util.print_i('Step2.1:正在读取新的学生数据')
    student_list = database.student_select(occam_conn, 'student_%s' % semester)
    util.print_i('Step2.2:正在写入新的学生数据')
    rowcount += util.multiprocess(task=database.entity_student_insert, main_data=student_list, max_thread=30,
                                  attach_data={'semester': semester, 'mysql_database': util.mysql_entity_database},
                                  multithread=util.mysql_multithread)

    util.print_t('Step3:正在拷贝卡片数据')

    util.print_i('Step3.1:正在删除旧的卡片数据')
    rowcount += database.entity_semester_delete(entity_conn, 'card', semester)
    util.print_i('Step3.2:正在读取新的卡片数据')
    card_list = database.occam_card_select(occam_conn, semester)
    util.print_i('Step3.3:正在写入新的卡片数据')
    rowcount += util.multiprocess(task=database.entity_card_insert, main_data=card_list, max_thread=30,
                                  attach_data={'semester': semester, 'mysql_database': util.mysql_entity_database},
                                  multithread=util.mysql_multithread)

    util.print_t('Step4:正在拷贝教室数据')

    util.print_i('Step4.1:正在读取新的教室数据')
    room_list = database.room_select(occam_conn, 'room_all')
    util.print_i('Step4.2:正在写入新的教室数据')
    rowcount += database.room_update(entity_conn, 'room', room_list)

    util.print_t('Step5:正在拷贝关联数据')

    util.print_i('Step5.1:正在删除旧的关联数据')
    rowcount += database.entity_semester_delete(entity_conn, 'teacher_link', semester)
    rowcount += database.entity_semester_delete(entity_conn, 'student_link', semester)
    util.print_i('Step5.2:正在读取新的关联数据')
    link_list = database.occam_link_select(occam_conn, semester)
    util.print_i('Step5.3:正在写入新的关联数据')
    rowcount += util.multiprocess(task=database.entity_link_insert, main_data=link_list, max_thread=30,
                                  attach_data={'semester': semester, 'mysql_database': util.mysql_entity_database},
                                  multithread=util.mysql_multithread)
