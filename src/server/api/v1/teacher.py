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


@blueprint.route('/teacher')
def hello_teacher():
    return 'Hello Teacher!'


@blueprint.route('/teacher/<string:identifier>/<string:semester>', methods=['GET'])
def get_teacher_schedule(identifier, semester):
    """
    通过老师资源ID和学期获取老师某学期的课程表
    :param identifier: 老师资源标识
    :param semester: 需要查询的学期
    :return: 该老师在该学期的课程
    """
    # 获取附加参数
    accept = request.values.get('accept')

    # 尝试解码老师资源标识
    try:
        id_type, id_code = util.identifier_decrypt(util.aes_key, identifier)
    except ValueError:
        abort(400)
        return

    # 检验数据的正确性
    if id_type != 'teacher' or util.check_semester(semester) is not True:
        abort(400)

    # 从数据库中访问老师数据
    teacher_schedule = dao.teacher_schedule(app.mysql_pool.connection(), id_code, semester)

    # 对资源编号进行对称加密
    for course in teacher_schedule['course']:
        course['cid'] = util.identifier_encrypt(util.aes_key, 'klass', course['cid'])
        course['rid'] = util.identifier_encrypt(util.aes_key, 'room', course['rid'])
        for teacher in course['teacher']:
            teacher['tid'] = util.identifier_encrypt(util.aes_key, 'teacher', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(teacher_schedule)
    else:
        return jsonify(teacher_schedule)
