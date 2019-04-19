# -*- coding: UTF-8 -*-
# Common package
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


def teacher_insert(teacher_data):
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
            sql = "SELECT `cid` FROM `card_%s` WHERE `klassID`='%s';" % (teacher_data['semester'], card['klassID'])
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                conn.begin()
                sql = "LOCK TABLE `card_%s` WRITE;" % teacher_data['semester']
                cursor.execute(sql)
                sql = "INSERT INTO  `card_%s` (`name`, `teacher`, `week`, `lesson`, `room`, `klass`, " \
                      "`pick`, `hour`, `type`, `klassID`, `roomID`)" \
                      "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s', '%s') " \
                      "ON DUPLICATE KEY UPDATE `teacher`=CONCAT(`teacher`, ';%s');" \
                      % (teacher_data['semester'], card['name'], card['teacher'], card['week'],
                         card['lesson'], card['room'], card['klass'], card['pick'], card['hour'],
                         card['type'], card['klassID'], card['roomID'], card['teacher'])
                cursor.execute(sql)
                rowcount += cursor.rowcount
                sql = "UNLOCK TABLES;"
                cursor.execute(sql)
                conn.commit()
            sql = "SELECT `cid` FROM `card_%s` WHERE `klassID`='%s';" % (teacher_data['semester'], card['klassID'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]
            sql = "INSERT INTO `teacher_link_%s` (`tid`, `cid`) VALUES ('%s', '%s');" \
                  % (teacher_data['semester'], tid, cid)
            cursor.execute(sql)
            rowcount += cursor.rowcount

        return rowcount


def student_insert(student_data):
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
        sql = "SELECT `code`, `name`, `klass`, `deputy`, `campus` FROM `student_all` WHERE `code`='%s';" \
              % student_data['student_code']
        cursor.execute(sql)
        student_info = cursor.fetchone()
        if student_info is None:
            util.print_e('学号为%s的学生不在数据总表中' % student_data['student_code'])
            return 0
        sql = "INSERT INTO `student_%s` (`code`,`name`,`klass`,`deputy`,`campus`) VALUES ('%s','%s','%s','%s','%s');" \
              % (student_data['semester'], student_info[0], student_info[1],
                 student_info[2], student_info[3], student_info[4])
        cursor.execute(sql)
        sid = cursor.lastrowid
        rowcount += cursor.rowcount

        # 向数据库中添加卡片数据
        for card in student_data['table']:
            # 先完成一次查询，为是否锁表做判断
            sql = "SELECT `cid` FROM `card_%s` WHERE `klassID`='%s';" % (student_data['semester'], card['klassID'])
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                conn.begin()
                sql = "LOCK TABLE `card_%s` WRITE;" % student_data['semester']
                cursor.execute(sql)
                sql = "INSERT INTO  `card_%s` (`name`, `teacher`, `week`, `lesson`, `room`, `klass`, " \
                      "`pick`, `hour`, `type`, `klassID`, `roomID`)" \
                      "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s', '%s') " \
                      "ON DUPLICATE KEY UPDATE cid = cid;" \
                      % (student_data['semester'], card['name'], card['teacher'], card['week'],
                         card['lesson'], card['room'], card['klass'], card['pick'], card['hour'],
                         card['type'], card['klassID'], card['roomID'])
                cursor.execute(sql)
                rowcount += cursor.rowcount
                sql = "UNLOCK TABLES;"
                cursor.execute(sql)
                conn.commit()
            sql = "SELECT `cid` FROM `card_%s` WHERE `klassID`='%s';" % (student_data['semester'], card['klassID'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]
            sql = "INSERT INTO `student_link_%s` (`sid`, `cid`) VALUES ('%s', '%s');" \
                  % (student_data['semester'], sid, cid)
            cursor.execute(sql)
            rowcount += cursor.rowcount
            sql = "UNLOCK TABLES;"
            cursor.execute(sql)

        return rowcount
