# -*- coding: UTF-8 -*-
# Common package
import time
import json
import pymysql
from random import random
# Personal package
import util


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
        sql = "SELECT `code`, `name`, `unit`, `title`, `degree` FROM `all_teacher` WHERE `code`='%s';" \
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

        for card in teacher_data['table']:
            sql = "INSERT INTO  `card_%s` (`name`,`teacher`,`week`,`lesson`,`room`,`md5`,`pick`,`code`,`hour`,`type`)" \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', %d,'%s') " \
                  "ON DUPLICATE KEY UPDATE cid = cid;" \
                  % (teacher_data['semester'], card['course_name'], teacher_data['teacher_name'], card['week'],
                     card['lesson'], card['room'], card['md5'], card['pick'], card['code'], card['hour'], card['type'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
            sql = "SELECT `cid` FROM `card_%s` WHERE `md5`='%s';" % (teacher_data['semester'], card['md5'])
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

        for card in student_data['table']:
            sql = "INSERT INTO  `card_%s` (`name`,`teacher`,`week`,`lesson`,`room`,`md5`,`pick`,`code`,`hour`,`type`)" \
                  "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', %d,'%s') " \
                  "ON DUPLICATE KEY UPDATE cid = cid;" \
                  % (student_data['semester'], card['course_name'], student_data['teacher_name'], card['week'],
                     card['lesson'], card['room'], card['md5'], card['pick'], card['code'], card['hour'], card['type'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
            sql = "SELECT `cid` FROM `card_%s` WHERE `md5`='%s';" % (student_data['semester'], card['md5'])
            cursor.execute(sql)
            cid = cursor.fetchone()[0]

            sql = "INSERT INTO `student_link_%s` (`sid`, `cid`) VALUES ('%s', '%s');" \
                  % (student_data['semester'], sid, cid)
            cursor.execute(sql)
            rowcount += cursor.rowcount

        return rowcount

