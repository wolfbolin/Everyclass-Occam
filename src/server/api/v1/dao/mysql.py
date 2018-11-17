# -*- coding: utf-8 -*-
# Common package
import pymysql
from DBUtils.PooledDB import PooledDB
# Personal package
import util


# mysql_pool = PooledDB(creator=pymysql,
#                       mincached=1, maxcached=util.max_thread,
#                       maxconnections=util.max_thread,
#                       host=util.mysql_host,
#                       user=util.mysql_user,
#                       passwd=util.mysql_password,
#                       db=util.mysql_database,
#                       port=util.mysql_port,
#                       charset=util.mysql_charset)  # 建立MySQL连接池

def connect():
    conn = pymysql.connect(host=util.mysql_host, user=util.mysql_user, passwd=util.mysql_password,
                           db=util.mysql_database, port=util.mysql_port, charset=util.mysql_charset)
    conn.autocommit(1)  # 定义数据库不自动提交
    return conn
