# -*- coding: utf-8 -*-
# Common package
from flask import Flask
# Personal package
import api
import util

app = Flask(__name__)
app.register_blueprint(api.blueprint, url_prefix='/v1')

app.mysql_pool = util.mysql_pool()
app.mongo_pool = util.mongo_pool()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    util.set_semester_list(util.mysql_connect(), app.mongo_pool)
    util.print_t('数据库可用学期：' + ';'.join(util.get_semester_list(app.mongo_pool)))
    app.run(
        host='0.0.0.0',
        port=80
    )
