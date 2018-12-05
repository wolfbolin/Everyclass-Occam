# -*- coding: UTF-8 -*-
# Common package
import msgpack
from flask import abort
from flask import request
from flask import jsonify
from flask import current_app as app
# Personal package
import util
import api.v1.dao as dao
from api.v1 import blueprint


@blueprint.route('/room')
def hello_room():
    return 'Hello Room!'


@blueprint.route('/room/<string:identifier>/<string:semester>', methods=['GET'])
def get_room_schedule(identifier, semester):
    """
    通过教室资源ID和学期获取教室某学期的课程表
    :param identifier: 教室资源标识
    :param semester: 需要查询的学期
    :return: 该教室在该学期的课程
    """
    # 获取附加参数
    accept = request.values.get('accept')

    # 尝试解码教室资源标识
    try:
        id_type, id_code = util.identifier_decrypt(util.aes_key, identifier)
    except ValueError:
        abort(400)
        return

    # 检验数据的正确性
    if id_type != 'room' or util.check_semester(semester) is not True:
        abort(400)

    # 从数据库中访问老师数据
    room_schedule = dao.room_schedule(app.mysql_pool.connection(), id_code, semester)

    # 对资源编号进行对称加密
    for course in room_schedule['course']:
        course['cid'] = util.identifier_encrypt(util.aes_key, 'student', course['cid'])
        course['rid'] = util.identifier_encrypt(util.aes_key, 'student', course['rid'])
        for teacher in course['teacher']:
            teacher['tid'] = util.identifier_encrypt(util.aes_key, 'student', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(room_schedule)
    else:
        return jsonify(room_schedule)
