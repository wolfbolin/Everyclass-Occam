# -*- coding: UTF-8 -*-
# Common package
# Personal package
import util


def student_select(conn, semester):
    """
    获取某学期全部学生的信息
    :return: 学生信息数据
    """
    student_list = []
    with conn.cursor() as cursor:
        # 查询学生信息总数
        sql = 'SELECT COUNT(*) FROM `student_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询学生的信息
        sql = 'SELECT `code`, `name`, `klass`, `deputy` FROM `student_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, student in enumerate(result):
            student_list.append({
                'code': student[0],
                'name': student[1],
                'klass': student[2],
                'deputy': student[3],
            })
            util.process_bar(count + 1, data_count, '已查询%d条学生数据' % (count + 1))
        return student_list


def teacher_select(conn, semester):
    """
    获取某学期全部教师的信息
    :return: 教师信息数据
    """
    teacher_list = []
    with conn.cursor() as cursor:
        # 查询教师信息总数
        sql = 'SELECT COUNT(*) FROM `teacher_%s`;' % semester
        cursor.execute(sql)
        data_count = cursor.fetchone()[0]
        # 查询教师的信息
        sql = 'SELECT `code`, `name`, `unit`, `title` FROM `teacher_%s`;' % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, teacher in enumerate(result):
            teacher_list.append({
                'code': teacher[0],
                'name': teacher[1],
                'unit': teacher[2],
                'title': teacher[3],
            })
            util.process_bar(count + 1, data_count, '已查询%d条教师数据' % (count + 1))
        return teacher_list


def room_select(conn, semester):
    """
    查询所有教室的信息
    :return: 教室信息列表
    """
    room_list = []
    with conn.cursor() as cursor:
        # 查询教室数据
        sql = "SELECT `code`, `name`, `campus`, `building` FROM `room_all`;"
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, item in enumerate(result):
            room_list.append({
                'code': item[0],
                'name': item[1],
                'campus': item[2],
                'building': item[2],
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
        sql = "SELECT `cid`, `room`, `roomID` FROM `card_%s` WHERE " \
              "LENGTH( `roomID` ) > 0 AND `roomID` NOT IN ( SELECT `code` FROM `room_all` );" \
              % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, item in enumerate(result):
            error_list.append({
                'cid': item[0],
                'room': item[1],
                'roomID': item[2],
            })
            util.process_bar(count + 1, len(result), '已监测到%d条映射异常' % (count + 1))
        return error_list


def doubt_klass_list(conn, semester):
    """
    检查重复的课程信息
    :return: 整合的重复课程
    """
    doubt_list = []
    with conn.cursor() as cursor:
        # 查询异常数据
        sql = "SELECT `name`, `teacher`, `week`, `lesson`, `room`, `klass`, `pick`, `hour`, `type`, `roomID` " \
              "FROM `card_%s` GROUP BY `name`, `teacher`, `week`, `lesson`, `room`, `klass`, `pick`, " \
              "`hour`, `type`, `roomID` HAVING COUNT(*) > 1;" % semester
        cursor.execute(sql)
        result = cursor.fetchall()
        for count, item in enumerate(result):
            doubt_list.append({
                'name': item[0],
                'teacher': item[1],
                'week': item[2],
                'lesson': item[3],
                'room': item[4],
                'klass': item[5],
                'pick': item[6],
                'hour': item[7],
                'type': item[8],
                'roomID': item[9],
            })
            util.process_bar(count + 1, len(result), '已监测到%d条课程异常' % (count + 1))
        return doubt_list


def klass_map_list(conn, semester, doubt_list):
    """
    检索疑似错误的课程的映射
    :return: 课程映射表
    """
    klass_map = []
    with conn.cursor() as cursor:
        for item in doubt_list:
            # 根据重复的信息查询现有的课程编号cid
            sql = "SELECT `cid` FROM `card_%s` WHERE `name`='%s' AND `teacher`='%s' AND `week`='%s' AND `" \
                  "lesson`='%s' AND `room`='%s' AND `klass`='%s' AND `pick`=%s AND `hour`=%s AND `type`='%s' AND " \
                  "`roomID`='%s';" \
                  % (semester, item['name'], item['teacher'], item['week'], item['lesson'], item['room'], item['klass'],
                     item['pick'], item['hour'], item['type'], item['roomID'])
            cursor.execute(sql)
            result = cursor.fetchall()
            cid_list = []
            for cid in result:
                cid_list.append(cid[0])
            # 查询每个cid的映射列表
            map_list = {}
            for cid in cid_list:
                sql = "SELECT `sid` FROM `student_link_%s` WHERE `cid`=%s;" % (semester, cid)
                cursor.execute(sql)
                result = cursor.fetchall()
                sid_list = []
                for sid in result:
                    sid_list.append(sid[0])
                map_list[cid] = sid_list
            klass_map.append({
                'key': item,
                'map': map_list
            })
        return klass_map
