# -*- coding: UTF-8 -*-
# Common package
import json
import msgpack
from flask import abort
from flask import request
from flask import jsonify
from flask import current_app as app
# Personal package
import util
from api import blueprint


@blueprint.route('/student')
def hello_student():
    return 'Hello student!'


@blueprint.route('/student/<string:identifier>/<string:semester>', methods=['GET'])
def get_student_schedule(identifier, semester):
    """
    通过学生资源ID和学期获取学生某学期的课程表
    :param identifier: 学生资源标识
    :param semester: 需要查询的学期
    :return: 该学生在该学期的课程
    """
    # 尝试解码学生资源标识
    try:
        id_type, id_code = util.identifier_decrypt(identifier)
    except ValueError:
        abort(400, '查询的学生信息无法被识别')
        return

    # 检验数据的正确性
    if id_type != 'student' or util.check_semester(semester, app.mongo_pool) is not True:
        abort(400, '查询的信息无法被识别')
        return

    # 从MySQL数据库中访问学生课程数据
    conn = app.mysql_pool.connection()
    with conn.cursor() as cursor:
        sql = """
        SELECT 
        `card`.`name` as course_name,
        `card`.`klassID` as course_cid,
        `card`.`room` as course_room,
        `card`.`roomID` as course_rid,
        `card`.`week` as course_week,
        `card`.`lesson` as course_lesson,
        `teacher`.`code` as teacher_tid,
        `teacher`.`name` as teacher_name,
        `teacher`.`title` as teacher_title 
        FROM `student_%s` as student
        JOIN `student_link_%s` as s_link USING(sid) 
        JOIN `card_%s` as card USING(cid)
        JOIN `teacher_link_%s` as t_link USING(cid)
        JOIN `teacher_%s` as teacher USING(tid)
        WHERE student.`code` = '%s';
        """ % (semester, semester, semester, semester, semester, id_code)
        cursor.execute(sql)
        course_info = {}
        for data in cursor.fetchall():
            if data[1] not in course_info:
                course_data = {
                    'name': data[0],
                    'cid': data[1],
                    'room': data[2],
                    'rid': data[3],
                    'week': json.loads(data[4]),
                    'lesson': data[5],
                    'teacher': []
                }
                course_info[data[1]] = course_data
            teacher_data = {
                'tid': data[6],
                'name': data[7],
                'title': data[8],
            }
            course_info[data[1]]['teacher'].append(teacher_data)

    # 从MongoDB数据库中访问学生课程数据
    mongo_db = app.mongo_pool['student']
    mongo_data = mongo_db.find_one({'code': id_code}, {'_id': 0})
    # 将聚合后的数据转换为序列
    student_data = {
        'sid': id_code,
        'name': mongo_data['name'],
        'class': mongo_data['klass'],
        'deputy': mongo_data['deputy'],
        'course': list(course_info.values())
    }

    # 获取附加参数并根据参数调整传输的数据内容
    accept = request.values.get('accept')
    week_string = request.values.get('week_string')
    other_semester = request.values.get('other_semester')
    # 对于课程周次的显示参数处理
    for course in student_data['course']:
        if week_string:
            course['week_string'] = util.make_week(course['week'])
    # 对于其他可用周次的显示参数处理
    if other_semester:
        student_data['semester_list'] = mongo_data['semester']

    # 对资源编号进行对称加密
    for course in student_data['course']:
        course['cid'] = util.identifier_encrypt('klass', course['cid'])
        course['rid'] = util.identifier_encrypt('room', course['rid'])
        for teacher in course['teacher']:
            teacher['tid'] = util.identifier_encrypt('teacher', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(student_data)
    else:
        return jsonify(student_data)
