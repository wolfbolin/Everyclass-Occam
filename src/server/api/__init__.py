# -*- coding: UTF-8 -*-
# Common package
from flask import jsonify
from flask import Blueprint

# Personal package
blueprint = Blueprint('api', __name__)
from .klass import hello_klass, get_klass_schedule
from .room import hello_room, get_room_schedule
from .search import hello_search, get_search
from .student import hello_student, get_student_schedule
from .teacher import hello_teacher, get_teacher_schedule


# 访问参数异常处理
@blueprint.errorhandler(400)
def bad_request(error):
    return jsonify({'message': str(error)}), 400


# 查询的资源不存在
@blueprint.errorhandler(404)
def bad_request(error):
    return jsonify({'message': str(error)}), 404
