# -*- coding: UTF-8 -*-
# Common package
import json
import pymysql
# Personal package
import util


def change_log_insert(conn, change_log):
    """
    写入该学期的修正日志
    :param conn: 数据库连接句柄
    :param change_log: 修正信息
    :return: 受影响的数据条数
    """
    mongo_db = conn['change_log']
    result = mongo_db.insert_many(
        list({
                 'semester': it['semester'],
                 'type': it['type'],
                 'message': it['message'],
             } for it in change_log)
    )
    return len(result.inserted_ids)


def occam_teacher_insert(teacher_data):
    """
    多线程处理函数
    根据教师课表中的教师工号向某学期的数据表中添加教师，数据来自数据总表
    :param teacher_data: 数据库连接句柄 + 学期信息 + 教师课表
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = teacher_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 先将老师从数据总表中添加到本学期数据表
        sql = "SELECT `code`, `name`, `unit`, `title`, `degree` FROM `teacher_all` WHERE `code`='%s';" \
              % teacher_data['teacher_code']
        cursor.execute(sql)
        teacher_info = cursor.fetchone()
        if teacher_info is None:
            util.print_e('工号为%s的教师不在数据总表中' % teacher_data['teacher_code'])
            return 0
        sql = "INSERT INTO `teacher_%s` (`code`,`name`,`unit`,`title`,`degree`) VALUES ('%s','%s','%s','%s','%s');" \
              % (teacher_data['semester'], teacher_info[0], teacher_info[1],
                 teacher_info[2], teacher_info[3], teacher_info[4])
        cursor.execute(sql)
        tid = cursor.lastrowid
        rowcount += cursor.rowcount

        # 向数据库中添加卡片数据
        for card in teacher_data['table']:
            # 先完成一次查询，为是否锁表做判断
            sql = "SELECT `cid` FROM `card_%s` WHERE `code`='%s';" % (teacher_data['semester'], card['code'])
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                conn.begin()
                sql = "LOCK TABLE `card_%s` WRITE;" % teacher_data['semester']
                cursor.execute(sql)
                sql = "INSERT INTO  `card_%s` (`pick`, `hour`, `type`, `code`, `name`, `room`, `week`, `lesson`, " \
                      "`teacher`, `tea_class`, `room_code`)" \
                      "VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') " \
                      "ON DUPLICATE KEY UPDATE `teacher`=CONCAT(`teacher`, ';%s');" \
                      % (teacher_data['semester'], card['pick'], card['hour'], card['type'],
                         card['code'], card['name'], card['room'], card['week'], card['lesson'],
                         card['teacher'], card['tea_class'], card['room_code'], teacher_data['teacher_name'])
                cursor.execute(sql)
                rowcount += cursor.rowcount
                sql = "UNLOCK TABLES;"
                cursor.execute(sql)
                conn.commit()
            sql = "SELECT `cid` FROM `card_%s` WHERE `code`='%s';" % (teacher_data['semester'], card['code'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]
            sql = "INSERT INTO `teacher_link_%s` (`tid`, `cid`) VALUES ('%s', '%s');" \
                  % (teacher_data['semester'], tid, cid)
            cursor.execute(sql)
            rowcount += cursor.rowcount

        return rowcount


def occam_student_insert(student_data):
    """
    多线程处理函数
    根据学生课表中的学生工号向某学期的数据表中添加学生，数据来自数据总表
    :param student_data: 数据库连接句柄 + 学期信息 + 学生课表
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = student_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 先将学生从数据总表中添加到本学期数据表
        sql = "SELECT `code`, `name`, `class`, `deputy`, `campus` FROM `student_all` WHERE `code`='%s';" \
              % student_data['student_code']
        cursor.execute(sql)
        student_info = cursor.fetchone()
        if student_info is None:
            util.print_e('学号为%s的学生不在数据总表中' % student_data['student_code'])
            return 0
        sql = "INSERT INTO `student_%s` (`code`,`name`,`class`,`deputy`,`campus`) VALUES ('%s','%s','%s','%s','%s');" \
              % (student_data['semester'], student_info[0], student_info[1],
                 student_info[2], student_info[3], student_info[4])
        cursor.execute(sql)
        sid = cursor.lastrowid
        rowcount += cursor.rowcount

        # 向数据库中添加卡片数据
        for card in student_data['table']:
            # 先完成一次查询，为是否锁表做判断
            sql = "SELECT `cid` FROM `card_%s` WHERE `code`='%s';" % (student_data['semester'], card['code'])
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                conn.begin()
                sql = "LOCK TABLE `card_%s` WRITE;" % student_data['semester']
                cursor.execute(sql)
                sql = "INSERT INTO  `card_%s` (`pick`, `hour`, `type`, `code`, `name`, `room`, `week`, `lesson`, " \
                      "`teacher`, `tea_class`, `room_code`)" \
                      "VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '', '%s', '%s') " \
                      "ON DUPLICATE KEY UPDATE `cid` = `cid`;" \
                      % (student_data['semester'], card['pick'], card['hour'], card['type'],
                         card['code'], card['name'], card['room'], card['week'], card['lesson'],
                         card['tea_class'], card['room_code'])
                cursor.execute(sql)
                rowcount += cursor.rowcount
                sql = "UNLOCK TABLES;"
                cursor.execute(sql)
                conn.commit()
            sql = "SELECT `cid` FROM `card_%s` WHERE `code`='%s';" % (student_data['semester'], card['code'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]
            sql = "INSERT INTO `student_link_%s` (`sid`, `cid`) VALUES ('%s', '%s');" \
                  % (student_data['semester'], sid, cid)
            cursor.execute(sql)
            rowcount += cursor.rowcount
            sql = "UNLOCK TABLES;"
            cursor.execute(sql)

        return rowcount


def entity_teacher_insert(teacher_data):
    """
    多线程处理函数
    向数据库中写入该学期的教师信息，不应该有冲突
    :param teacher_data: 数据库连接句柄 + 学期信息
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = teacher_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 写入拷贝数据
        try:
            sql = "INSERT INTO `teacher` (`code`,`name`,`unit`,`title`,`degree`) VALUES ('%s','%s','%s','%s','%s')" \
                  % (teacher_data['code'], teacher_data['name'], teacher_data['unit'],
                     teacher_data['title'], teacher_data['degree'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
        except pymysql.err.IntegrityError as e:
            sql = "UPDATE `teacher` SET `name`='%s', `unit`='%s', `title`='%s', `degree`='%s' WHERE `code`='%s'" \
                  % (teacher_data['name'], teacher_data['unit'], teacher_data['title'],
                     teacher_data['degree'], teacher_data['code'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
    return rowcount


def entity_student_insert(student_data):
    """
    多线程处理函数
    向数据库中写入该学期的学生信息，不应该有冲突
    :param student_data: 数据库连接句柄 + 数据
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = student_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 写入拷贝数据
        try:
            sql = "INSERT INTO `student` (`code`, `name`, `class`, `deputy`, `campus`) " \
                  "VALUES ('%s','%s','%s','%s','%s')" \
                  % (student_data['code'], student_data['name'], student_data['class'],
                     student_data['deputy'], student_data['campus'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
        except pymysql.err.IntegrityError as e:
            sql = "UPDATE `student` SET `name`='%s', `class`='%s', `deputy`='%s', `campus`='%s' WHERE `code`='%s'" \
                  % (student_data['name'], student_data['class'], student_data['deputy'],
                     student_data['campus'], student_data['code'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
    return rowcount


def entity_card_insert(card_data):
    """
    多线程处理函数
    向数据库中写入该学期的卡片信息，不应该有冲突
    :param card_data: 数据库连接句柄 + 数据
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = card_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        sql = "INSERT INTO `card` (`oid`, `pick`, `hour`, `type`, `code`, `name`, `room`, `week`, `lesson`, " \
              "`teacher`, `tea_class`, `room_code`, `course_code`, `semester`) " \
              "VALUES (%d, %d, %d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" \
              % (card_data['cid'], card_data['pick'], card_data['hour'], card_data['type'], card_data['code'],
                 card_data['name'], card_data['room'], card_data['week'], card_data['lesson'], card_data['teacher'],
                 card_data['tea_class'], card_data['room_code'], card_data['course_code'], card_data['semester'])
        cursor.execute(sql)
        rowcount += cursor.rowcount
    return rowcount


def entity_link_insert(link_data):
    """
    多线程处理函数
    向数据库中写入该学期的卡片信息，不应该有冲突
    :param link_data: 数据库连接句柄 + 数据
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = link_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 判读关联数据类型
        if 'tid' in link_data.keys():
            # 教师类型关联，查询原始数据的新编号
            sql = "SELECT `tid` FROM `teacher` WHERE `code`='%s';" % link_data['teacher_code']
            cursor.execute(sql)
            tid = cursor.fetchone()[0]
            sql = "SELECT `cid` FROM `card` WHERE `semester`='%s' AND `code`='%s';" \
                  % (link_data['semester'], link_data['card_code'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]
            # 写入新的关联数据
            sql = "INSERT INTO `teacher_link` (`tid`, `cid`, `semester`) VALUES (%d, %d, '%s')" \
                  % (tid, cid, link_data['semester'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
        elif 'sid' in link_data.keys():
            # 学生类型关联，查询原始数据的新编号
            sql = "SELECT `sid` FROM `student` WHERE `code`='%s';" % link_data['student_code']
            cursor.execute(sql)
            sid = cursor.fetchone()[0]
            sql = "SELECT `cid` FROM `card` WHERE `semester`='%s' AND `code`='%s';" \
                  % (link_data['semester'], link_data['card_code'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]
            # 写入新的关联数据
            sql = "INSERT INTO `student_link` (`sid`, `cid`, `semester`) VALUES (%d, %d, '%s')" \
                  % (sid, cid, link_data['semester'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
    return rowcount
