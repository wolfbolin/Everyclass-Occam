# -*- coding: UTF-8 -*-
# Common package
import msgpack
from flask import abort
from flask import request
from flask import jsonify
from flask import current_app as app
# Personal package
import util
from api import blueprint


@blueprint.route('/search')
def hello_search():
    return 'Hello search!'


@blueprint.route('/search/<string:keyword>', methods=['GET'])
def get_search(keyword):
    """
    通过关键字在数据库中搜索相关的信息
    :param keyword: 搜索的关键字
    :return: 搜索结果
    """
    # 获取附加参数
    accept = request.values.get('accept')

    # 打开数据库连接
    conn = app.mysql_pool.connection()
    with conn.cursor() as cursor:
        # 查询学生信息
        sql = """
        SELECT 
        `student_all`.`name` as student_name, 
        `student_all`.`klass` as student_klass, 
        `student_all`.`deputy` as student_deputy
        FROM `student_all`
        WHERE `code` = %s OR `name` = %s;
        """
        cursor.execute(sql, (keyword, keyword,))
        result = cursor.fetchall()

        util.print_t(result)

    return "OK"
