# -*- coding: utf-8 -*-
# Common package
import pymongo
import pymysql
from flask import Flask
from DBUtils.PooledDB import PooledDB
# Personal package
import api
import util

app = Flask(__name__)
app.register_blueprint(api.blueprint, url_prefix='/v1')

mysql_pool = PooledDB(creator=pymysql,
                      mincached=1, maxcached=util.max_thread,
                      maxconnections=util.max_thread,
                      host=util.mysql_host,
                      user=util.mysql_user,
                      passwd=util.mysql_password,
                      db=util.mysql_database,
                      port=util.mysql_port,
                      charset=util.mysql_charset)  # 建立MySQL连接池

mongo_pool = pymongo.MongoClient(host=util.mongo_host,
                                 port=util.mongo_port,
                                 username=util.mongo_user,
                                 password=util.mongo_password
                                 )[util.mongo_database]

app.mysql_pool = mysql_pool
app.mongo_pool = mongo_pool


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=80
    )
