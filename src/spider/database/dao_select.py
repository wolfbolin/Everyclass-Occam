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
                'sid': student[0],
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
                'tid': teacher[0],
                'name': teacher[1],
                'unit': teacher[2],
                'title': teacher[3],
            })
            util.process_bar(count + 1, data_count, '已查询%d条教师数据' % (count + 1))
        return teacher_list
