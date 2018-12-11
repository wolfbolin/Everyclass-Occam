# -*- coding: UTF-8 -*-
"""
该文件内保存程序在运行时必要的密钥信息
在部署程序时需要根据需要调整该文件中的配置
"""

# MySQL连接配置
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_user = 'defaultuser'
mysql_charset = 'utf8mb4'
mysql_password = 'defaultpasswd'
mysql_database = 'defaultdatabase'

# MongoDB连接配置
mongo_host = '127.0.0.1'
mongo_port = 27017
mongo_user = 'defaultuser'
mongo_password = 'defaultpasswd'
mongo_database = 'defaultdatabase'

# 预定义数据
base_headers = {
    'Host': '',
    'Connection': '',
    'User-Agent': '',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
}

# 教务系统首页
csujwc_url = ''

# CAS身份认证页面
kblogin_url = ''

# 各类课表查询-教师
sykb_url = ''

# 教师信息列表查询接口
pklb_url = ''

# 教师课表数据查询接口
kbkb_url = ''

# 学生信息列表查询接口
xskb_url = ''

# 学生查询数据查询接口
kbkb_url = ''

# 所有教师的信息查询接口
jgs_url = ''

# 所有学生的信息查询接口
usa_url = ''

# 所有教室的信息查询接口
jspk_url = ''
