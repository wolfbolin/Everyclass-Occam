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


@blueprint.route('/course')
def hello_klass():
    return 'Hello Course!'


@blueprint.route('/course/<string:identifier>/<string:semester>', methods=['GET'])
def get_klass_schedule(identifier, semester):
    """
    通过课程资源ID和学期获取课程某学期的信息表
    :param identifier: 课程资源标识
    :param semester: 需要查询的学期
    :return: 该课程的资源信息表
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
    if id_type != 'klass' or util.check_semester(semester) is not True:
        abort(400)

    # 从数据库中访问老师数据
    course_schedule = dao.klass_schedule(app.mysql_pool.connection(), id_code, semester)

    # 对资源编号进行对称加密
    course_schedule['rid'] = util.identifier_encrypt(util.aes_key, 'room', course_schedule['rid'])
    for student in course_schedule['student']:
        student['sid'] = util.identifier_encrypt(util.aes_key, 'student', student['sid'])
    for teacher in course_schedule['teacher']:
        teacher['tid'] = util.identifier_encrypt(util.aes_key, 'student', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(course_schedule)
    else:
        return jsonify(course_schedule)
