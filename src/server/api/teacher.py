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


@blueprint.route('/teacher')
def hello_teacher():
    return 'Hello teacher!'


@blueprint.route('/teacher/<string:identifier>/<string:semester>', methods=['GET'])
def get_teacher_schedule(identifier, semester):
    """
    通过老师资源ID和学期获取老师某学期的课程表
    :param identifier: 老师资源标识
    :param semester: 需要查询的学期
    :return: 该老师在该学期的课程
    """
    # 尝试解码老师资源标识
    try:
        id_type, id_code = util.identifier_decrypt(util.aes_key, identifier)
    except ValueError:
        abort(400, '查询的教师信息无法被识别')
        return

    # 检验数据的正确性
    if id_type != 'teacher' or util.check_semester(semester) is not True:
        abort(400, '查询的信息无法被识别')
        return

    # 从数据库中访问老师数据
    conn = app.mysql_pool.connection()
    with conn.cursor() as cursor:
        sql = """
        SELECT 
        `teacher`.`name` as teacher_name, 
        `teacher`.`title` as teacher_title, 
        `teacher`.`unit` as teacher_unit, 
        `card`.`name` as course_name,
        `card`.`klassID` as course_cid,
        `card`.`room` as course_room,
        `card`.`roomID` as course_rid,
        `card`.`week` as course_week,
        `card`.`lesson` as course_lesson,
        `o_teacher`.`name` as other_teacher_name, 
        `o_teacher`.`title` as other_teacher_title, 
        `o_teacher`.`code` as teacher_tid
        FROM `teacher_%s` as teacher
        JOIN `teacher_link_%s` as teacher2card 
        ON teacher.tid = teacher2card.tid AND teacher.code = '%s'
        JOIN `card_%s` as card ON teacher2card.cid = card.cid
        JOIN `teacher_link_%s` as card2teacher ON card.cid = card2teacher.cid
        JOIN `teacher_%s` as o_teacher ON card2teacher.tid = o_teacher.tid;
        """ % (semester, semester, id_code, semester, semester, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        teacher_data = {}
        teacher_info = True
        course_info = {}
        for data in result:
            if teacher_info:
                teacher_info = False
                teacher_data['name'] = data[0]
                teacher_data['title'] = data[1]
                teacher_data['unit'] = data[2]
            if data[4] not in course_info:
                course_data = {
                    'name': data[3],
                    'cid': data[4],
                    'room': data[5],
                    'rid': data[6],
                    'week': data[7],
                    'lesson': data[8],
                    'teacher': []
                }
                course_info[data[4]] = course_data
            o_teacher_data = {
                'name': data[9],
                'title': data[10],
                'tid': data[11]
            }
            course_info[data[4]]['teacher'].append(o_teacher_data)
        # 将聚合后的数据转换为序列
        teacher_data['course'] = list(course_info.values())

    # 获取附加参数并根据参数调整传输的数据内容
    accept = request.values.get('accept')
    week_string = request.values.get('week_string')
    other_semester = request.values.get('other_semester')
    # 对于课程周次的显示参数处理
    for course in teacher_data['course']:
        if week_string is True:
            course['week_string'] = util.make_week(course['week'])
    # 对于其他可用周次的显示参数处理
    if other_semester is True:
        mongo_db = app.mongo_pool['teacher']
        result = mongo_db.find_one({'tid': id_code}, {'_id': 0})
        teacher_data['semester_list'] = result['semester']

    # 对资源编号进行对称加密
    for course in teacher_data['course']:
        course['cid'] = util.identifier_encrypt(util.aes_key, 'klass', course['cid'])
        course['rid'] = util.identifier_encrypt(util.aes_key, 'room', course['rid'])
        for teacher in course['teacher']:
            teacher['tid'] = util.identifier_encrypt(util.aes_key, 'teacher', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(teacher_data)
    else:
        return jsonify(teacher_data)
