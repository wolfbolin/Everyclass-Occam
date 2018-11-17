# -*- coding: UTF-8 -*-
# Common package
import msgpack
from flask import abort
from flask import request
from flask import jsonify
# Personal package
import util
import api.v1.dao as dao
from api.v1 import blueprint


@blueprint.route('/')
def hello_world():
    return 'Hello World!'


@blueprint.route('/student/<string:identifier>/<string:semester>', methods=['GET'])
def get_student_schedule(identifier, semester):
    """
    通过学生资源ID和学期获取学生某学期的课程表
    :param identifier: 学生资源标识
    :param semester: 需要查询的学期
    :return: 该学生在该学期的课程
    """
    # 获取附加参数
    accept = request.values.get('accept')

    # 尝试解码学生资源标识
    try:
        id_type, id_code = util.identifier_decrypt(util.aes_key, identifier)
    except ValueError:
        abort(400)
        return

    # 检验数据的正确性
    if id_type != 'student' or util.check_semester(semester) is not True:
        abort(400)

    # 从数据库中访问学生数据
    student_schedule = dao.student_schedule(dao.connect(), id_code, semester)

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(student_schedule)
    else:
        return jsonify(student_schedule)
