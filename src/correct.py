# -*- coding: utf-8 -*-
# Common package
import pymysql
from warnings import filterwarnings
# Personal package
import database
import builder
import filter
import util

# 将数据库警告定义为错误方便捕获
filterwarnings('error', category=pymysql.Warning)

if __name__ == "__main__":
    util.print_w('请自行完成数据库同步操作')

    document = input("更新所有学期错误数据or更新某学期错误数据(y/20xx-20xx-x/other)：")
    semester_list = []
    if document == 'y':
        # 检索数据库中已有的学期
        mysql_conn = database.mysql_connect(util.mysql_entity_database)
        semester_list = database.get_semester_list(mysql_conn)
        mysql_conn.close()
    elif filter.check_semester(document) is True:
        semester_list = document
    else:
        util.print_e('请做出正确的选择')
        exit()

    rowcount = 0
    change_log = []

    for semester in semester_list:
        util.print_w('正在修改%s学期的异常数据' % semester)

        # 修正教室数据
        sql_count, change_log_room = builder.correct_room_data(semester)
        rowcount += sql_count
        change_log.extend(change_log_room)

        # 修正课程数据
        count, change_log_klass = builder.correct_klass_data(semester)
        rowcount += sql_count
        change_log.extend(change_log_klass)

        # 写入修改日志
        builder.save_change_log(semester, change_log)

        # 重建搜索数据
        builder.build_search_semester(semester)
