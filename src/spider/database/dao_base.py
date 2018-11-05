# -*- coding: UTF-8 -*-
# Common package
import pymysql
# Personal package
import util


def connect():
    conn = pymysql.connect(host=util.mysql_host, user=util.mysql_user, passwd=util.mysql_password,
                           db=util.mysql_database, port=util.mysql_port, charset=util.mysql_charset)
    conn.autocommit(1)  # 定义数据库不自动提交
    return conn


def clean_table(conn, table_name):
    """
    清除指定数据表中的数据
    :param conn: 数据库连接句柄
    :param table_name: 需要清除的数据表名称
    :return: 受影响的数据条数
    """
    with conn.cursor() as cursor:
        cursor.execute("START TRANSACTION;")  # 开启事务
        sql = "TRUNCATE TABLE `{}`;".format(table_name)
        cursor.execute(sql)
        rowcount = cursor.rowcount
        return rowcount


def remove_tables(conn, semester):
    util.print_i('正在删除本学期数据表')
    tables = util.table_name_template.copy()
    for table in tables:
        try:
            with conn.cursor() as cursor:
                sql = "DROP TABLE IF EXISTS `{}`".format(table.format(semester))
                cursor.execute(sql)  # DDL操作会自动提交
        except pymysql.Warning as w:
            util.print_e('数据库警告:{}'.format(w))


def add_tables(conn, semester):
    util.print_i('正在添加本学期数据表')
    tables = util.table_name_template.copy()
    for table in tables:
        with conn.cursor() as cursor:
            sql = "CREATE TABLE `{}` LIKE `{}`".format(table.format(semester), table.format("template"))
            cursor.execute(sql)  # DDL操作会自动提交


def add_foreign(conn, semester):
    util.print_i('正在添加数据表外键')
    with conn.cursor() as cursor:
        fk1 = '''ALTER TABLE `teacher_link_{}` 
                 ADD CONSTRAINT `fk1_{}`
                 FOREIGN KEY (`tid`) 
                 REFERENCES `teacher_{}` (`tid`) 
                 ON DELETE NO ACTION 
                 ON UPDATE NO ACTION;'''.format(semester, semester, semester)
        cursor.execute(fk1)
        fk2 = '''ALTER TABLE `teacher_link_{}`
                 ADD CONSTRAINT `fk2_{}`
                 FOREIGN KEY (`cid`)
                 REFERENCES `card_{}` (`cid`)
                 ON DELETE NO ACTION
                 ON UPDATE NO ACTION;'''.format(semester, semester, semester)
        cursor.execute(fk2)
        fk3 = '''ALTER TABLE `student_link_{}`
                 ADD CONSTRAINT `fk3_{}`
                 FOREIGN KEY (`sid`) 
                 REFERENCES `student_{}` (`sid`) 
                 ON DELETE NO ACTION 
                 ON UPDATE NO ACTION;'''.format(semester, semester, semester)
        cursor.execute(fk3)
        fk4 = '''ALTER TABLE `student_link_{}`
                 ADD CONSTRAINT `fk4_{}`
                 FOREIGN KEY (`cid`)
                 REFERENCES `card_{}` (`cid`)
                 ON DELETE NO ACTION
                 ON UPDATE NO ACTION;'''.format(semester, semester, semester)
        cursor.execute(fk4)


def get_teacher_title(conn):
    """
    获取数据库中全部教师的职称
    :param conn: 数据库连接句柄
    :return: 以排序好的教师职称
    """
    result = []
    with conn.cursor() as cursor:
        sql = "SELECT DISTINCT title FROM `all_teacher`;"
        cursor.execute(sql)
        for row in cursor.fetchall():
            result.append(row[0])
        result.sort(key=cmp, reverse=True)
        return result


def cmp(elem):
    return len(elem)
