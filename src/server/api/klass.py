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


@blueprint.route('/course')
def hello_klass():
    return 'Hello course!'


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
        abort(400, '查询的课程信息无法被识别')
        return

    # 检验数据的正确性
    if id_type != 'klass' or util.check_semester(semester) is not True:
        abort(400, '查询的信息无法被识别')
        return

    # 从数据库中访问老师数据
    conn = app.mysql_pool.connection()
    with conn.cursor() as cursor:
        # 查询课程的基础信息
        sql = """
        SELECT 
        `card`.`name` as course_name,
        `card`.`room` as course_room,
        `card`.`roomID` as course_rid,
        `card`.`week` as course_week,
        `card`.`lesson` as course_lesson,
        `card`.`klass` as course_klass,
        `card`.`pick` as course_pick,
        `card`.`hour` as course_hour,
        `card`.`type` as course_type 
        FROM `card_%s` as `card`
        WHERE klassID = '%s';
        """ % (semester, id_code)
        cursor.execute(sql)
        result = cursor.fetchone()
        klass_data = {
            'name': result[0],
            'room': result[1],
            'rid': result[2],
            'week': json.loads(result[3]),
            'lesson': result[4],
            'class': result[5],
            'pick': result[6],
            'hour': result[7],
            'type': result[8],
            'student': [],
            'teacher': []
        }
        # 查询课程的学生信息
        sql = """
        SELECT 
        `student`.`name` as student_name, 
        `student`.`klass` as student_klass, 
        `student`.`code` as student_code 
        FROM `card_%s` as card
        JOIN `student_link_%s` as s_link 
        ON card.cid = s_link.cid AND card.klassID = '%s' 
        JOIN `student_%s` as student USING(sid)
        """ % (semester, semester, id_code, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        for data in result:
            student_data = {
                'name': data[0],
                'class': data[1],
                'sid': data[2]
            }
            klass_data['student'].append(student_data)
        # 查询课程的教师信息
        sql = """
        SELECT 
        `teacher`.`name` as student_name, 
        `teacher`.`title` as student_title, 
        `teacher`.`code` as student_code 
        FROM `card_%s` as card
        JOIN `teacher_link_%s` as t_link 
        ON card.cid = t_link.cid AND card.klassID = '%s' 
        JOIN `teacher_%s` as teacher USING(tid)
        """ % (semester, semester, id_code, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        for data in result:
            teacher_data = {
                'name': data[0],
                'title': data[1],
                'tid': data[2]
            }
            klass_data['teacher'].append(teacher_data)

    # 获取附加参数并根据参数调整传输的数据内容
    accept = request.values.get('accept')
    week_string = request.values.get('week_string')
    # 对于课程周次的显示参数处理
    if week_string is 'True':
        klass_data['week_string'] = util.make_week(klass_data['week'])

    # 对资源编号进行对称加密
    klass_data['rid'] = util.identifier_encrypt(util.aes_key, 'room', klass_data['rid'])
    for student in klass_data['student']:
        student['sid'] = util.identifier_encrypt(util.aes_key, 'student', student['sid'])
    for teacher in klass_data['teacher']:
        teacher['tid'] = util.identifier_encrypt(util.aes_key, 'student', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(klass_data)
    else:
        return jsonify(klass_data)
