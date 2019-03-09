# -*- coding: utf-8 -*-
# Common package
import time
import json
from math import ceil
# Personal package
import util
import spider
import filter
import database


def build_teacher():
    """
    全盘考虑所有教师的数据获取与写入
    :return: rowcount
    """
    util.print_a('开始处理所有教师的数据')
    rowcount = 0
    cookie = spider.cookie()

    util.print_t('Step1:正在获取所有教师的数据')
    if util.query_from_cache('global', '', 'teacher_all'):
        teacher_all = util.read_from_cache('global', '', 'teacher_all')
        teacher_all = json.loads(teacher_all)
        util.print_d('已从缓存中读取数据')
    else:
        teacher_all = spider.teacher_all(cookie, 5)
        util.save_to_cache('global', '', 'teacher_all', json.dumps(teacher_all))
        util.print_d('已从网络获取数据并缓存')

    # 数据过滤代码片段
    util.print_t('Step2:正在校验所有教师的数据')
    teacher_all = filter.teacher_all(teacher_all)

    # 向数据库中写入数据
    util.print_t('Step3:正在写入所有教师的数据')
    time_start = time.time()
    rowcount += util.multiprocess(task=database.teacher_update, main_data=teacher_all,
                                  multithread=util.mysql_multithread, max_thread=10)
    time_end = time.time()
    util.print_d('教师数据写入数据库完成，耗时%d秒，操作数据库%d行' % (ceil(time_end - time_start), rowcount))

    util.print_d('所有教师的数据已处理完毕')
    return rowcount


def build_teacher_table(semester):
    """
    全盘考虑所有教师课表的数据获取与写入
    :param semester: 学期信息
    :return: rowcount
    """
    util.print_a('开始处理所有教师课表的数据')
    rowcount = 0
    cookie = spider.cookie()

    util.print_t('Step1:正在获取本学期开课教师列表')
    if util.query_from_cache(semester, '', 'teacher_list'):
        teacher_list = util.read_from_cache(semester, '', 'teacher_list')
        teacher_list = json.loads(teacher_list)
        util.print_d('已从缓存中读取数据')
    else:
        teacher_list = spider.teacher_list(semester, cookie)
        util.save_to_cache(semester, '', 'teacher_list', json.dumps(teacher_list))
        util.print_d('已从网络获取数据并缓存')

    # 二次获取数据
    util.print_t('Step2:正在获取本学期开课教师课表')

    util.print_i('Step2.1:正在检索缺少的课表数据')
    download_list = []
    for count, teacher in enumerate(teacher_list):
        if util.query_from_cache(semester, 'teacher_html', teacher['jgh'].replace('*', '#')) is False:
            download_list.append(teacher)
        util.process_bar(count + 1, len(teacher_list), '已检索%d条课表数据' % (count + 1))
    util.print_d('根据检索结果还需要下载%d条记录' % len(download_list))

    util.print_i('Step2.2:正在下载缺少的课表数据')
    if len(download_list) == 0:
        util.print_i('无需下载，跳过该步骤')
    else:
        time_start = time.time()
        util.multiprocess(task=spider.teacher_table, main_data=download_list, multithread=util.nosql_multithread,
                          attach_data={'semester': semester, 'cookie': cookie}, max_thread=1)  # 该处线程数不可过多
        time_end = time.time()
        util.print_d('本学期教师授课信息已经下载完毕，已缓存，耗时%d秒' % ceil(time_end - time_start))

    # 数据过滤代码片段
    util.print_t('Step3:正在解析并范化本学期开课教师数据')

    util.print_i('Step3.1:正在解析并范化教师名单')
    teacher_list = filter.teacher_list(teacher_list)

    util.print_i('Step3.2:正在解析并范化教师课表数据')
    if util.query_from_cache(semester, '', 'teacher_table'):
        teacher_table = util.read_from_cache(semester, '', 'teacher_table')
        teacher_table = json.loads(teacher_table)
        util.print_d('已从缓存中读取数据')
    else:
        teacher_table = util.multiprocess(task=filter.teacher_table, main_data=teacher_list,
                                          multithread=util.nosql_multithread,
                                          attach_data={'semester': semester}, max_thread=5)
        util.save_to_cache(semester, '', 'teacher_table', json.dumps(teacher_table))
        util.print_d('已从缓存中解析并缓存')

    # 将数据写入数据库
    util.print_t('Step4:正在写入本学期教师课表信息')
    time_start = time.time()
    sql_count = util.multiprocess(task=database.teacher_insert, main_data=teacher_table, max_thread=10,
                                  attach_data={'semester': semester}, multithread=util.mysql_multithread)
    time_end = time.time()
    util.print_d('本学期教师信息写入数据库完成，耗时%d秒，操作数据库%d行' % (ceil(time_end - time_start), sql_count))
    rowcount += sql_count

    util.print_d('本学期教师数据已处理完毕')
    return rowcount
