# -*- coding: UTF-8 -*-
# Common package
# Personal package
import util


def occam_student_select(conn, semester):
    """
    在Occam数据库中查询某学期全部学生的信息
    :return: 学生信息数据
    """
    student_list = []
    with conn.cursor() as cursor:
        # 查询学生信息总数
        sql = 'SELECT COUNT(*) FROM `student_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询学生的信息
        sql = 'SELECT `sid`, `code`, `name`, `class`, `deputy`, `campus` FROM `student_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, student in enumerate(result):
            student_list.append({
                'sid': student[0],
                'code': student[1],
                'name': student[2],
                'class': student[3],
                'deputy': student[4],
                'campus': student[5]
            })
            util.process_bar(count + 1, data_count, '已查询%d条学生数据' % (count + 1))
        return student_list


def occam_teacher_select(conn, semester):
    """
    在Occam数据库中查询某学期全部教师的信息
    :return: 教师信息数据
    """
    teacher_list = []
    with conn.cursor() as cursor:
        # 查询教师信息总数
        sql = 'SELECT COUNT(*) FROM `teacher_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询教师的信息
        sql = 'SELECT `tid`, `code`, `name`, `unit`, `title`, `degree` FROM `teacher_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, teacher in enumerate(result):
            teacher_list.append({
                'tid': teacher[0],
                'code': teacher[1],
                'name': teacher[2],
                'unit': teacher[3],
                'title': teacher[4],
                'degree': teacher[5]
            })
            util.process_bar(count + 1, data_count, '已查询%d条教师数据' % (count + 1))
        return teacher_list


def occam_card_select(conn, semester):
    """
    在Occam数据库中查询某学期所有的卡片信息
    :return: 卡片信息
    """
    card_list = []
    with conn.cursor() as cursor:
        # 查询卡片信息总数
        sql = 'SELECT COUNT(*) FROM `card_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询卡片的信息
        sql = 'SELECT `cid`, `pick`, `hour`, `type`, `code`, `name`, `room`, `week`, `lesson`, `teacher`, ' \
              '`tea_class`, `room_code`, `course_code` FROM `card_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, teacher in enumerate(result):
            card_list.append({
                'cid': teacher[0],
                'pick': teacher[1],
                'hour': teacher[2],
                'type': teacher[3],
                'code': teacher[4],
                'name': teacher[5],
                'room': teacher[6],
                'week': teacher[7],
                'lesson': teacher[8],
                'teacher': teacher[9],
                'tea_class': teacher[10],
                'room_code': teacher[11],
                'course_code': teacher[12],
            })
            util.process_bar(count + 1, data_count, '已查询%d条卡片数据' % (count + 1))
        return card_list


def occam_link_select(conn, semester):
    """
    在Occam数据库中查询某学期全部教师的信息
    :return: 教师信息数据
    """
    link_list = []
    with conn.cursor() as cursor:
        # 查询教师关联信息总数
        sql = 'SELECT COUNT(*) FROM `teacher_link_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询教师的信息
        sql = 'SELECT `tid`, `cid` FROM `teacher_link_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, teacher in enumerate(result):
            link_list.append({
                'tid': teacher[0],
                'cid': teacher[1]
            })
            util.process_bar(count + 1, data_count, '已查询%d条教师关联数据' % (count + 1))

        # 查询学生关联信息总数
        sql = 'SELECT COUNT(*) FROM `student_link_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询学生关联的信息
        sql = 'SELECT `sid`, `cid` FROM `student_link_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, teacher in enumerate(result):
            link_list.append({
                'sid': teacher[0],
                'cid': teacher[1]
            })
            util.process_bar(count + 1, data_count, '已查询%d条学生关联数据' % (count + 1))

        return link_list


def entity_student_select(conn, semester):
    """
    在Occam数据库中查询某学期全部学生的信息
    :return: 学生信息数据
    """
    student_list = []
    with conn.cursor() as cursor:
        # 查询学生信息总数
        sql = "SELECT COUNT(*) FROM `student` WHERE `semester`='%s';" % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询学生的信息
        sql = "SELECT `code`, `name`, `class`, `deputy`, `campus` FROM `student` WHERE `semester`='%s';" % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, student in enumerate(result):
            student_list.append({
                'code': student[0],
                'name': student[1],
                'class': student[2],
                'deputy': student[3],
                'campus': student[4]
            })
            util.process_bar(count + 1, data_count, '已查询%d条学生数据' % (count + 1))
        return student_list


def entity_teacher_select(conn, semester):
    """
    在Entity数据库中查询某学期全部教师的信息
    :return: 教师信息数据
    """
    teacher_list = []
    with conn.cursor() as cursor:
        # 查询教师信息总数
        sql = "SELECT COUNT(*) FROM `teacher` WHERE `semester`='%s';" % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询教师的信息
        sql = "SELECT `code`, `name`, `unit`, `title`, `degree` FROM `teacher` WHERE `semester`='%s';" % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, teacher in enumerate(result):
            teacher_list.append({
                'code': teacher[0],
                'name': teacher[1],
                'unit': teacher[2],
                'title': teacher[3],
                'degree': teacher[4]
            })
            util.process_bar(count + 1, data_count, '已查询%d条教师数据' % (count + 1))
        return teacher_list


def room_select(conn, table):
    """
    查询所有教室的信息
    :return: 教室信息列表
    """
    room_list = []
    with conn.cursor() as cursor:
        # 查询教室数据
        sql = "SELECT `code`, `name`, `campus`, `building` FROM `%s`;" % table
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, item in enumerate(result):
            room_list.append({
                'code': item[0],
                'name': item[1],
                'campus': item[2],
                'building': item[3],
            })
            util.process_bar(count + 1, len(result), '已读取到%d条教室数据' % (count + 1))
        return room_list


def regex_room_select(conn, room_converter):
    """
    利用正则抽取教室信息
    :param conn: 数据库连接
    :param room_converter: 正则列表
    :return: 教室信息列表
    """
    room_list = []
    with conn.cursor() as cursor:
        for converter in room_converter:
            # 查询教室数据
            sql = "SELECT `code`, `name`, `campus`, `building` FROM `room` WHERE `name` REGEXP '^%s$';" \
                  % converter['regex']
            cursor.execute(sql)
            result = cursor.fetchall()
            for count, item in enumerate(result):
                room_list.append({
                    'regex': converter['regex'],
                    'pattern': converter['pattern'],
                    'type': converter['type'],
                    'code': item[0],
                    'name': item[1],
                    'campus': item[2],
                    'building': item[3],
                })
                util.process_bar(count + 1, len(result), '已读取到%d条教室数据' % (count + 1))
    return room_list


def error_room_select(conn, semester):
    """
    检查无法映射的教室编号
    :return: 异常数据列表
    """
    error_list = []
    with conn.cursor() as cursor:
        # 查询异常数据
        sql = "SELECT `cid`, `room`, `room_code` FROM `card` WHERE `semester`='%s' AND " \
              "LENGTH( `room_code` ) > 0 AND `room_code` NOT IN ( SELECT `code` FROM `room` );" \
              % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, item in enumerate(result):
            error_list.append({
                'cid': item[0],
                'room': item[1],
                'room_code': item[2],
            })
            util.process_bar(count + 1, len(result), '已监测到%d条映射异常' % (count + 1))
        return error_list


def doubt_card_list(conn, semester):
    """
    检查重复的课程信息
    :return: 整合的重复课程
    """
    doubt_list = []
    with conn.cursor() as cursor:
        # 查询异常数据
        sql = "SELECT `name`, `teacher`, `week`, `lesson`, `room`, `pick`, `hour`, `type`, `tea_class`, `room_code` " \
              "FROM `card` WHERE `semester`='%s' GROUP BY `name`, `teacher`, `week`, `lesson`, `room`, " \
              "`pick`, `hour`, `type`, `tea_class`, `room_code` HAVING COUNT(*) > 1;" % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, item in enumerate(result):
            doubt_list.append({
                'name': item[0],
                'teacher': item[1],
                'week': item[2],
                'lesson': item[3],
                'room': item[4],
                'pick': item[5],
                'hour': item[6],
                'type': item[7],
                'tea_class': item[8],
                'room_code': item[9],
            })
            util.process_bar(count + 1, len(result), '已监测到%d条课程异常' % (count + 1))
        return doubt_list


def card_map_list(conn, semester, doubt_list):
    """
    检索疑似错误的课程的映射
    :return: 课程映射表
    """
    card_map = []
    with conn.cursor() as cursor:
        for item in doubt_list:
            # 根据重复的信息查询现有的课程编号cid
            sql = "SELECT `cid` FROM `card` WHERE `semester`='%s' AND `name`='%s' AND `teacher`='%s' AND `week`='%s' " \
                  "AND `lesson`='%s' AND `room`='%s' AND `tea_class`='%s' AND `pick`=%s AND `hour`=%s " \
                  "AND `type`='%s' AND `room_code`='%s';" \
                  % (semester, item['name'], item['teacher'], item['week'], item['lesson'], item['room'],
                     item['tea_class'], item['pick'], item['hour'], item['type'], item['room_code'])
            cursor.execute(sql)
            result = cursor.fetchall()
            cid_list = []
            for cid in result:
                cid_list.append(cid[0])
            # 查询每个cid的映射列表
            map_list = {}
            for cid in cid_list:
                sql = "SELECT `sid` FROM `student_link` WHERE `cid`=%s;" % cid
                cursor.execute(sql)
                result = cursor.fetchall()
                sid_list = []
                for sid in result:
                    sid_list.append(sid[0])
                map_list[cid] = sid_list
            card_map.append({
                'key': item,
                'map': map_list
            })
        return card_map
