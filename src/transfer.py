# -*- coding: utf-8 -*-
# Common package
import pymysql
from warnings import filterwarnings
# Personal package
import database
import builder
import util

# 将数据库警告定义为错误方便捕获
filterwarnings('error', category=pymysql.Warning)

if __name__ == "__main__":
    # 预读取学期列表
    mysql_conn = database.mysql_connect(util.mysql_occam_database)
    semester_list = database.get_semester_list(mysql_conn)
    mysql_conn.close()

    # 获取操作指令
    document = input("更新所有学期数据or更新某学期数据(y/20xx-20xx-x/other)：")
    if document == 'y':
        # 清空数据库课程信息，使主键从1开始计算
        builder.build_entity_table()
        pass
    elif document in semester_list:
        semester_list = [document]
    else:
        util.print_e('请做出正确的选择')
        exit()

    rowcount = 0
    change_log = []

    for semester in semester_list:
        util.print_w('正在修改%s学期的数据' % semester)

        # 同步学期数据
        builder.copy_mysql_data(semester)

        # 修正教室数据
        sql_count, change_log_room = builder.correct_room_data(semester)
        rowcount += sql_count
        change_log.extend(change_log_room)

        # 修正课程数据
        sql_count, change_log_klass = builder.correct_klass_data(semester)
        rowcount += sql_count
        change_log.extend(change_log_klass)

        # 写入修改日志
        sql_count = builder.save_change_log(semester, change_log)
        rowcount += sql_count

        # 重建搜索数据
        sql_count = builder.build_search_base(semester)
        rowcount += sql_count

    util.print_d('操作完成，共计修改数据库%s行' % rowcount)
