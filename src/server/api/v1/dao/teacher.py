# -*- coding: utf-8 -*-
# Common package
import copy
# Personal package
import util


def teacher_schedule(conn, code, semester):
    """
    根据学期与教师学号实现对教师课表的查询
    :param conn: 数据库连接
    :param code: 教师学号
    :param semester: 查询的学期
    :return: 课表数据
    """
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
        """ % (semester, semester, code, semester, semester, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        teacher_data = copy.deepcopy(util.teacher_data)
        teacher_info = True
        course_info = {}
        for data in result:
            if teacher_info:
                teacher_info = False
                teacher_data['name'] = data[0]
                teacher_data['title'] = data[1]
                teacher_data['unit'] = data[2]
            if data[4] not in course_info:
                course_data = copy.deepcopy(util.course_data)
                course_data['name'] = data[3]
                course_data['cid'] = data[4]
                course_data['room'] = data[5]
                course_data['rid'] = data[6]
                course_data['week'] = data[7]
                course_data['lesson'] = data[8]
                course_data['teacher'] = []
                course_info[data[4]] = course_data
            o_teacher_data = copy.deepcopy(util.teacher_data)
            o_teacher_data['name'] = data[9]
            o_teacher_data['title'] = data[10]
            o_teacher_data['tid'] = data[11]
            course_info[data[4]]['teacher'].append(o_teacher_data)
        # 将聚合后的数据转换为序列
        teacher_data['course'] = list(course_info.values())
        return teacher_data
