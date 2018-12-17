# -*- coding: UTF-8 -*-
# Common package
import re
import json
import msgpack
from flask import abort
from flask import request
from flask import jsonify
from flask import current_app as app
# Personal package
import util
from api import blueprint


@blueprint.route('/room')
def hello_room():
    return 'Hello room!'


@blueprint.route('/room/<string:identifier>/<string:semester>', methods=['GET'])
def get_room_schedule(identifier, semester):
    """
    通过教室资源ID和学期获取教室某学期的课程表
    :param identifier: 教室资源标识
    :param semester: 需要查询的学期
    :return: 该教室在该学期的课程
    """
    # 尝试解码教室资源标识
    try:
        id_type, id_code = util.identifier_decrypt(identifier)
    except ValueError:
        abort(400, '查询的教室信息无法被识别')
        return

    # 检验数据的正确性
    if id_type != 'room' or util.check_semester(semester, app.mongo_pool) is not True:
        abort(400, '查询的信息无法被识别')
        return

    # 从数据库中访问老师数据
    conn = app.mysql_pool.connection()
    with conn.cursor() as cursor:
        sql = """
        SELECT 
        `room`.`name` as room_name, 
        `room`.`building` as room_building, 
        `room`.`campus` as room_campus, 
        `card`.`name` as course_name,
        `card`.`klassID` as course_cid,
        `card`.`room` as course_room,
        `card`.`roomID` as course_rid,
        `card`.`week` as course_week,
        `card`.`lesson` as course_lesson,
        `teacher`.`code` as teacher_tid,
        `teacher`.`name` as teacher_name,
        `teacher`.`title` as teacher_title 
        FROM `room_all` as room
        LEFT JOIN `card_%s` as card ON room.code = card.roomID 
        LEFT JOIN `teacher_link_%s` as t_link USING(cid)
        LEFT JOIN `teacher_%s` as teacher USING(tid) 
        WHERE room.code = '%s'
        """ % (semester, semester, semester, id_code)
        cursor.execute(sql)
        result = cursor.fetchall()
        room_data = {}
        room_info = True
        course_info = {}
        for data in result:
            if room_info:
                room_info = False
                room_data['rid'] = id_code
                room_data['name'] = data[0]
                room_data['building'] = data[1]
                room_data['campus'] = data[2]
            if data[4] not in course_info:
                course_data = {
                    'name': data[3],
                    'cid': data[4],
                    'room': data[5],
                    'rid': data[6],
                    'week': json.loads(data[7]),
                    'lesson': data[8],
                    'teacher': []
                }
                course_info[data[4]] = course_data
            teacher_data = {
                'tid': data[9],
                'name': data[10],
                'title': data[11],
            }
            if teacher_data['tid']:
                course_info[data[4]]['teacher'].append(teacher_data)
        # 将聚合后的数据转换为序列
        room_data['course'] = list(course_info.values())

    # 获取附加参数并根据参数调整传输的数据内容
    accept = request.values.get('accept')
    week_string = request.values.get('week_string')
    other_semester = request.values.get('other_semester')
    # 对于课程周次的显示参数处理
    for course in room_data['course']:
        if week_string:
            course['week_string'] = util.make_week(course['week'])
    # 对于其他可用周次的显示参数处理
    if other_semester:
        room_data['semester_list'] = util.get_semester_list(app.mongo_pool)

    # 对资源编号进行对称加密
    for course in room_data['course']:
        course['cid'] = util.identifier_encrypt('klass', course['cid'])
        course['rid'] = util.identifier_encrypt('room', course['rid'])
        for teacher in course['teacher']:
            if teacher['tid']:
                teacher['tid'] = util.identifier_encrypt('teacher', teacher['tid'])

    # 根据请求类型反馈数据
    if accept == 'msgpack':
        return msgpack.dumps(room_data)
    else:
        return jsonify(room_data)
