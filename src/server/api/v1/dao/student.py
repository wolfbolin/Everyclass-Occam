# -*- coding: utf-8 -*-
# Common package
import copy
# Personal package
import util


def student_schedule(conn, code, semester):
    """
    根据学期与学生学号实现对学生课表的查询
    :param conn: 数据库连接
    :param code: 学生学号
    :param semester: 查询的学期
    :return: 课表数据
    """
    with conn.cursor() as cursor:
        sql = """
        SELECT 
        `student`.`name` as student_name, 
        `student`.`klass` as student_klass, 
        `student`.`deputy` as student_deputy, 
        `card`.`name` as course_name,
        `card`.`klassID` as course_cid,
        `card`.`room` as course_room,
        `card`.`roomID` as course_rid,
        `card`.`week` as course_week,
        `card`.`lesson` as course_lesson,
        `teacher`.`name` as teacher_name,
        `teacher`.`title` as teacher_title,
        `teacher`.`code` as teacher_tid
        FROM `student_%s` as student
        JOIN `student_link_%s` as s_link 
        ON student.sid = s_link.sid AND student.code = '%s'
        JOIN `card_%s` as card USING(cid)
        JOIN `teacher_link_%s` as t_link USING(cid)
        JOIN `teacher_%s` as teacher USING(tid);
        """ % (semester, semester, code, semester, semester, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        student_data = copy.deepcopy(util.student_data)
        student_info = True
        course_info = {}
        for data in result:
            if student_info:
                student_info = False
                student_data['name'] = data[0]
                student_data['klass'] = data[1]
                student_data['deputy'] = data[2]
            if data[4] not in course_info:
                course_data = copy.deepcopy(util.course_data)
                course_data['name'] = data[3]
                course_data['cid'] = data[4]
                course_data['room'] = data[5]
                course_data['rid'] = data[6]
                course_data['week'] = data[7]
                course_data['lesson'] = data[8]
                course_info[data[4]] = course_data
            teacher_data = copy.deepcopy(util.teacher_data)
            teacher_data['name'] = data[9]
            teacher_data['title'] = data[10]
            teacher_data['tid'] = data[11]
            course_info[data[4]]['teacher'].append(teacher_data)
        # 将聚合后的数据转换为序列
        student_data['course'] = list(course_info.values())
        return student_data




