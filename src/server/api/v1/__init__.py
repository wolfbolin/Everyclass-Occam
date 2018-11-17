# -*- coding: UTF-8 -*-
# Common package
from flask import jsonify
from flask import Blueprint

# Personal package
blueprint = Blueprint('api_v1', __name__)
from .student import get_student_schedule


# 访问参数异常处理
@blueprint.errorhandler(400)
def bad_request(error):
    return jsonify({'message': str(error)}), 400


# 查询的资源不存在
@blueprint.errorhandler(404)
def bad_request(error):
    return jsonify({'message': str(error)}), 404