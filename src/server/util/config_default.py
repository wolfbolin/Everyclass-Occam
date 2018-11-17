# -*- coding: UTF-8 -*-
"""
系统运行时读取的配置文件
在部署程序时，需要根据需要调整该配置文件中的参数
"""

# 资源标识AES计算密钥
aes_key = '123456789'

# MySQL连接池的配置数据
max_thread = 4

# MySQL连接配置
mysql_host = '127.0.0.1'
mysql_user = 'defaultuser'
mysql_password = 'defaultpasswd'
mysql_database = 'defaultdatabase'
mysql_port = 3306
mysql_charset = 'utf8'
