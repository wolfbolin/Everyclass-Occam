# -*- coding: utf-8 -*-
# Common package
import json
import time
from math import ceil
# Personal package
import util
import filter
import spider
import database


def build_course_info(semester):
    """
    为每个课程记录（card）补充课程相关信息
    :param semester: 需要补充的学期
    :return: rowcount
    """
    util.print_a('开始补充本学期课程信息')
    rowcount = 0
    cookie = spider.cookie()

    util.print_t('Step1:正在获取本学期课程信息')
    if util.query_from_cache(semester, '', 'course_list'):
        course_list = util.read_from_cache(semester, '', 'course_list')
        course_list = json.loads(course_list)
        util.print_d('已从缓存中读取数据')
    else:
        course_list = spider.course_list(semester, cookie)
        util.save_to_cache(semester, '', 'course_list', json.dumps(course_list))
        util.print_d('已从网络获取数据并缓存')

    # 数据过滤代码片段
    util.print_t('Step2:正在解析并范化本学期课程信息')

    util.print_i('Step2.1:正在解析并范化课程信息')
    course_list = filter.course_list(course_list)

    # 将数据写入数据库
    util.print_t('Step3:正在写入本学期学生课表信息')
    time_start = time.time()
    sql_count = util.multiprocess(task=database.course_code_update, main_data=course_list, max_thread=20,
                                  attach_data={'semester': semester, 'mysql_database': util.mysql_occam_database},
                                  multithread=util.mysql_multithread)
    time_end = time.time()
    util.print_d('本学期学生信息写入数据库完成，耗时%d秒，操作数据库%d行' % (ceil(time_end - time_start), sql_count))
    rowcount += sql_count

    util.print_d('本学期学生数据已处理完毕')
    return rowcount


