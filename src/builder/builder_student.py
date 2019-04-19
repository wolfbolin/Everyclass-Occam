# -*- coding: utf-8 -*-
# Common package
import gc
import time
import json
from math import ceil
# Personal package
import util
import spider
import filter
import database


def build_student():
    """
    全盘考虑所有学生的数据获取与写入
    :return: rowcount
    """
    util.print_a('开始处理所有学生的数据')
    rowcount = 0
    cookie = spider.cookie()

    util.print_t('Step1:正在获取所有学生的数据')
    if util.query_from_cache('global', '', 'student_all'):
        student_all = util.read_from_cache('global', '', 'student_all')
        student_all = json.loads(student_all)
        util.print_d('已从缓存中读取数据')
    else:
        student_all = spider.student_all(cookie, 5)
        util.save_to_cache('global', '', 'student_all', json.dumps(student_all))
        util.print_d('已从网络获取数据并缓存')

    # 数据过滤代码片段
    util.print_t('Step2:正在校验所有学生的数据')
    student_all = filter.student_all(student_all)

    # 向数据库中写入数据
    util.print_t('Step3:正在写入所有学生的数据')
    time_start = time.time()
    rowcount += util.multiprocess(task=database.student_update, main_data=student_all,
                                  multithread=util.mysql_multithread, max_thread=10,
                                  attach_data={'mysql_database': util.mysql_occam_database})
    time_end = time.time()
    util.print_d('学生数据写入数据库完成，耗时%d秒，操作数据库%d行' % (ceil(time_end - time_start), rowcount))

    util.print_d('所有学生的数据已处理完毕')
    return rowcount


def build_student_table(semester):
    """
    全盘考虑所有学生课表的数据获取与写入
    :param semester: 学期信息
    :return: rowcount
    """
    util.print_a('开始处理本学期学生课表数据')
    rowcount = 0
    cookie = spider.cookie()

    util.print_t('Step1:正在获取本学期上课学生数据')
    if util.query_from_cache(semester, '', 'student_list'):
        student_list = util.read_from_cache(semester, '', 'student_list')
        student_list = json.loads(student_list)
        util.print_d('已从缓存中读取数据')
    else:
        student_list = spider.student_list(semester=semester, cookie=cookie)
        util.save_to_cache(semester, '', 'student_list', json.dumps(student_list))
        util.print_d('已从网络获取数据并缓存')

    # 二次获取数据
    util.print_t('Step2:正在获取本学期上课学生的课表数据')

    util.print_i('Step2.1:正在检索缺少的课表数据')
    download_list = []
    for count, student in enumerate(student_list):
        if util.query_from_cache(semester, 'student_html', student['xh']) is False:
            download_list.append(student)
        util.process_bar(count + 1, len(student_list), '已检索%d条课表数据' % (count + 1))
    util.print_d('根据检索结果还需要下载%d条记录' % len(download_list))

    util.print_i('Step2.2:正在下载缺少的课表数据')
    if len(download_list) == 0:
        util.print_i('无需下载，跳过该步骤')
    else:
        time_start = time.time()
        util.multiprocess(task=spider.student_table, main_data=download_list, multithread=util.nosql_multithread,
                          attach_data={'semester': semester, 'cookie': cookie}, max_thread=1)  # 该处线程数不可过多
        time_end = time.time()
        util.print_d('本学期学生上课信息已经下载完毕，已缓存，耗时%d秒' % ceil(time_end - time_start))

    # 数据过滤代码片段
    util.print_t('Step3:正在解析并范化本学期上课学生数据')

    util.print_i('Step3.1:正在解析并范化学生名单')
    student_list = filter.student_list(student_list)

    util.print_i('Step3.2:正在解析并范化学生课表数据')
    if util.query_from_cache(semester, '', 'student_table'):
        util.print_i('正在从缓存中读取大文件')
        student_table = util.read_from_cache(semester, '', 'student_table')
        student_table = json.loads(student_table)
        util.print_d('已从缓存中读取数据')
    else:
        student_table = util.multiprocess(task=filter.student_table, main_data=student_list,
                                          multithread=util.nosql_multithread,
                                          attach_data={'semester': semester}, max_thread=10)
        util.print_i('Step3.3:正在回收内存资源...让电脑喘口气')
        time.sleep(2)
        gc.collect()
        time.sleep(2)
        util.print_i('Step3.4:向本地缓存中写入数据')
        util.save_to_cache(semester, '', 'student_table', json.dumps(student_table))
        util.print_d('已从缓存中解析并缓存')

    # 将数据写入数据库
    util.print_t('Step4:正在写入本学期学生课表信息')
    time_start = time.time()
    sql_count = util.multiprocess(task=database.occam_student_insert, main_data=student_table, max_thread=20,
                                  attach_data={'semester': semester, 'mysql_database': util.mysql_occam_database},
                                  multithread=util.mysql_multithread)
    time_end = time.time()
    util.print_d('本学期学生信息写入数据库完成，耗时%d秒，操作数据库%d行' % (ceil(time_end - time_start), sql_count))
    rowcount += sql_count

    util.print_d('本学期学生数据已处理完毕')
    return rowcount
