# -*- coding: utf-8 -*-
# Common package
import pymysql
from warnings import filterwarnings
# Personal package
import builder

# 将数据库警告定义为错误方便捕获
filterwarnings('error', category=pymysql.Warning)

if __name__ == "__main__":
    # 完成所有学期搜索信息的更新
    document = input("更新所有学期搜索数据库(y/n)：")
    if document is 'y':
        builder.build_search_all()
        exit()

    # 完成所有学期搜索信息的更新
    document = input("更新所有学期错误教室(y/n)：")
    if document is 'y':
        builder.correct_error_data_all()
        exit()
