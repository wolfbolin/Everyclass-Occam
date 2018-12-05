# -*- coding: utf-8 -*-
# Common package
import copy
# Personal package
import util


def klass_schedule(conn, code, semester):
    """
    根据学期与课程编号实现对课程课表的查询
    :param conn: 数据库连接
    :param code: 教师学号
    :param semester: 查询的学期
    :return: 课表数据
    """
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
        """ % (semester, code)
        cursor.execute(sql)
        result = cursor.fetchone()
        klass_data = copy.deepcopy(util.klass_data)
        klass_data['name'] = result[0]
        klass_data['room'] = result[1]
        klass_data['rid'] = result[2]
        klass_data['week'] = result[3]
        klass_data['lesson'] = result[4]
        klass_data['klass'] = result[5]
        klass_data['pick'] = result[6]
        klass_data['hour'] = result[7]
        klass_data['type'] = result[8]
        klass_data['student'] = []
        klass_data['teacher'] = []
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
        """ % (semester, semester, code, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        for data in result:
            student_data = copy.deepcopy(util.student_data)
            del student_data['deputy']
            student_data['name'] = data[0]
            student_data['klass'] = data[1]
            student_data['sid'] = data[2]
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
        """ % (semester, semester, code, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        for data in result:
            teacher_data = copy.deepcopy(util.teacher_data)
            del teacher_data['unit']
            teacher_data['name'] = data[0]
            teacher_data['title'] = data[1]
            teacher_data['tid'] = data[2]
            klass_data['teacher'].append(teacher_data)
        return klass_data
