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
        util.print_t('即将更新以下学期数据')
        util.print_i(' | '.join(semester_list))
        mongo_conn = database.mongo_connect(util.mongo_entity_database)
        database.clean_search(mongo_conn)
    elif document in semester_list:
        semester_list = [document]
    else:
        util.print_e('请做出正确的选择')
        exit()

    rowcount = 0

    for semester in semester_list:
        util.print_w('正在重建%s学期的搜索数据' % semester)

        # 重建搜索数据
        sql_count = builder.build_search_semester(semester)
        rowcount += sql_count

    util.print_d('操作完成，共计修改数据库%s行' % rowcount)
