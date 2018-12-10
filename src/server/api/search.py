# -*- coding: UTF-8 -*-
# Common package
import msgpack
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

    # 在学生关联表中搜索关键字
    mongo_db = app.mongo_pool['student']
    result = mongo_db.find(
        filter={'$or': [{'code': keyword}, {'name': keyword}]},
        projection={'_id': 0}
    ).sort('code')
    student_data = []
    for student in result:
        student_data.append({
            'sid': student['code'],
            'name': student['name'],
            'klass': student['klass'],
            'deputy': student['deputy'],
            'semester': student['semester']
        })

    # 在教师关联表中搜索关键字
    mongo_db = app.mongo_pool['teacher']
    result = mongo_db.find(
        filter={'$or': [{'code': keyword}, {'name': keyword}]},
        projection={'_id': 0}
    ).sort('code')
    teacher_data = []
    for teacher in result:
        teacher_data.append({
            'tid': teacher['code'],
            'name': teacher['name'],
            'unit': teacher['unit'],
            'semester': teacher['semester']
        })

    # 在教室表中搜索关键字
    conn = app.mysql_pool.connection()
    with conn.cursor() as cursor:
        sql = "SELECT  `code`, `name`, `campus`, `building` as room_building FROM `room_all` WHERE `name` = %s;"
        cursor.execute(sql, keyword)
        result = cursor.fetchone()
        if result:
            room_data = {
                'rid': result[0],
                'name': result[1],
                'campus': result[2],
                'building': result[3],
            }
        else:
            room_data = {}

    # 对资源编号进行对称加密
    for student in student_data:
        student['sid'] = util.identifier_encrypt(util.aes_key, 'student', student['sid'])
    for teacher in teacher_data:
        teacher['tid'] = util.identifier_encrypt(util.aes_key, 'teacher', teacher['tid'])
    if room_data:
        room_data['rid'] = util.identifier_encrypt(util.aes_key, 'room', room_data['rid'])

    # 根据请求类型反馈数据
    search_data = {
        'student': student_data,
        'teacher': teacher_data,
        'room': room_data
    }
    if accept == 'msgpack':
        return msgpack.dumps(search_data)
    else:
        return jsonify(search_data)
