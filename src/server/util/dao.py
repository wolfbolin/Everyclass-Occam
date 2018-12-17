# -*- coding: UTF-8 -*-
# Common package
import pymongo
import pymysql
from DBUtils.PooledDB import PooledDB
# Personal package
import util

"""
数据库连接与连接池的封装
"""


def mysql_connect():
    """
    建立单个MySQL数据库的连接
    :return: MySQL连接句柄
    """
    conn = pymysql.connect(host=util.get_config('mysql_host'),
                           user=util.get_config('mysql_user'),
                           passwd=util.get_config('mysql_password'),
                           db=util.get_config('mysql_database'),
                           port=util.get_config('mysql_port'),
                           charset=util.get_config('mysql_charset'))
    conn.autocommit(1)  # 定义数据库不自动提交
    return conn


def mysql_pool():
    """
    通过配置参数建立链接并生成连接池
    :return: MySQl连接池
    """
    pool = PooledDB(creator=pymysql,
                    mincached=util.get_config('min_thread'),
                    maxcached=util.get_config('max_thread'),
                    maxconnections=util.get_config('max_connect'),
                    host=util.get_config('mysql_host'),
                    user=util.get_config('mysql_user'),
                    passwd=util.get_config('mysql_password'),
                    db=util.get_config('mysql_database'),
                    port=util.get_config('mysql_port'),
                    charset=util.get_config('mysql_charset'))  # 建立MySQL连接池
    return pool


def mongo_pool():
    """
    通过配置参数建立链接并生成连接池
    :return:
    """
    pool = pymongo.MongoClient(host=util.get_config('mongo_host'),
                               port=util.get_config('mongo_port'),
                               username=util.get_config('mongo_user'),
                               password=util.get_config('mongo_password')
                               )[util.get_config('mongo_database')]
    return pool
