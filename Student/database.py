# coding=utf-8
import Util
import pymysql


# 多线程处理
def write_student_info(mysql_pool, task_data, cookies):
    conn = mysql_pool.connection()
    cursor = conn.cursor()

    sql = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
    cursor.execute(sql)

    rowcount = 0
    for times in range(3):
        try:
            # 写入分表信息
            sql = "REPLACE INTO `student` (`code`, `name`, `class`, `faculty`, `campus`, `version`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s)"
            # print(sql % (data["code"], data["name"], data["campus"], data["building"], data["version"]))
            cursor.execute(sql, args=[task_data["code"], task_data["name"], task_data["class"],
                                      task_data["faculty"], task_data["campus"], task_data["version"]])
            rowcount += cursor.rowcount

            # 获取教室编号
            sql = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql)
            sid = cursor.fetchone()[0]

            # 写入总表信息
            sql = "REPLACE INTO `entity` (`code`, `name`, `alias`, `group`, `obj_id`, `version`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s)"
            # print(sql % (data["code"], data["name"], "", "student", str(rid), data["version"]))
            cursor.execute(sql, args=[task_data["code"], task_data["name"], "", "student", str(sid), task_data["version"]])
            rowcount += cursor.rowcount
        except pymysql.err.OperationalError:
            Util.print_yellow("MySQL deadlock error. Retry [%d]" % (times + 1))
            conn.rollback()
            rowcount = 0
            continue
        break

    conn.commit()
    return rowcount
