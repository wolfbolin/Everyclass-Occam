# coding=utf-8
import Util
import pymysql


# 多线程处理
def write_room_info(mysql_pool, task_data, cookies):
    conn = mysql_pool.connection()
    cursor = conn.cursor()

    sql = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
    cursor.execute(sql)

    rowcount = 0
    for times in range(3):
        try:
            # 写入分表信息
            sql = "REPLACE INTO `room` (`code`, `name`, `campus`, `building`, `version`)" \
                  "VALUES (%s, %s, %s, %s, %s)"
            # print(sql % (data["code"], data["name"], data["campus"], data["building"], data["version"]))
            cursor.execute(sql, args=[task_data["code"], task_data["name"],
                                      task_data["campus"], task_data["building"], task_data["version"]])
            rowcount += cursor.rowcount

            # 获取教室编号
            sql = "SELECT LAST_INSERT_ID()"
            cursor.execute(sql)
            rid = cursor.fetchone()[0]

            # 写入总表信息
            sql = "REPLACE INTO `entity` (`code`, `name`, `alias`, `group`, `obj_id`, `version`)" \
                  "VALUES (%s, %s, %s, %s, %s, %s)"
            # print(sql % (data["code"], data["name"], "", "room", str(rid), data["version"]))
            cursor.execute(sql, args=[task_data["code"], task_data["name"], "", "room", str(rid), task_data["version"]])
            rowcount += cursor.rowcount
        except pymysql.err.OperationalError:
            Util.print_yellow("MySQL deadlock error. Retry [%d]" % (times + 1))
            conn.rollback()
            rowcount = 0
            continue
        break

    conn.commit()
    return rowcount


def read_room_info(conn, code_list):
    cursor = conn.cursor()

    sql = "SELECT `code`, `name`, `campus`, `building`, `version` FROM `room`"
    if code_list is not None:
        sql += "WHERE `code` IN ({})".format(", ".join(list("%s" for i in range(len(code_list)))))
    else:
        code_list = []
    cursor.execute(sql, args=code_list)

    room_list = []
    for result in cursor.fetchall():
        room_list.append({
            "code": result[0],
            "name": result[1],
            "campus": result[2],
            "building": result[3],
            "version": result[4],
        })

    Util.print_white("读取【教室】基础数据 [%d] 条" % len(room_list))
    return room_list
