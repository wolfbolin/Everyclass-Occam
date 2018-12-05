# -*- coding: utf-8 -*-
# Common package
import copy
# Personal package
import util


def room_schedule(conn, code, semester):
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
        `room`.`name` as room_name, 
        `room`.`building` as room_building, 
        `room`.`campus` as room_campus, 
        `card`.`name` as course_name,
        `card`.`klassID` as course_cid,
        `card`.`room` as course_room,
        `card`.`roomID` as course_rid,
        `card`.`week` as course_week,
        `card`.`lesson` as course_lesson,
        `teacher`.`name` as teacher_name,
        `teacher`.`title` as teacher_title,
        `teacher`.`code` as teacher_tid
        FROM `room_all` as room
        JOIN `card_%s` as card 
        ON room.code = card.roomID AND room.code = '%s'
        JOIN `teacher_link_%s` as t_link USING(cid)
        JOIN `teacher_%s` as teacher USING(tid);
        """ % (semester, code, semester, semester)
        cursor.execute(sql)
        result = cursor.fetchall()
        room_data = copy.deepcopy(util.room_data)
        room_info = True
        course_info = {}
        for data in result:
            if room_info:
                room_info = False
                room_data['name'] = data[0]
                room_data['building'] = data[1]
                room_data['campus'] = data[2]
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
        room_data['course'] = list(course_info.values())
        return room_data
