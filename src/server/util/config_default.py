# -*- coding: UTF-8 -*-
"""
系统运行时读取的配置文件
在部署程序时，需要根据需要调整该配置文件中的参数
"""

set_dict = {
    # 资源标识AES计算密钥
    'aes_key': 'aes_password',

    # MySQL连接池的配置数据
    'min_thread': 1,
    'max_thread': 10,
    'max_connect': 10,

    # MySQL连接配置
    'mysql_host': '127.0.0.1',
    'mysql_port': 3306,
    'mysql_user': 'default_user',
    'mysql_charset': 'utf8mb4',
    'mysql_password': 'default_password',
    'mysql_database': 'everyclass_occam',

    # MongoDB连接配置
    'mongo_host': '127.0.0.1',
    'mongo_port': 27017,
    'mongo_user': 'default_user',
    'mongo_password': 'default_password',
    'mongo_database': 'everyclass_occam'
}
