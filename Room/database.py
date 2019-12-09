# coding=utf-8
import Util
import pymysql


def read_room_list_html(conn, version):
    cursor = conn.cursor()
    sql = "SELECT `page`, `data` FROM `list_html` WHERE `group`='room' AND `version`=%s"
    cursor.execute(sql, args=[str(version)])

    room_list = []
    for result in cursor.fetchall():
        room_list.append({
            "page": result[0],
            "data": result[1]
        })

    Util.print_white("读取【教室列表】原始数据 [%d] 页" % len(room_list))
    return room_list


def write_room_list_html(conn, version, page, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `list_html` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), "room", str(version)])

    conn.commit()

    Util.print_white("插入【教室列表】原始数据 - 第 [%s] 页 (RC: %d)" % (page, cursor.rowcount))


def write_room_list_json(conn, version, page, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `list_json` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), "room", str(version)])

    conn.commit()

    Util.print_white("插入【教室列表】解析数据-第 [%s] 页 (RC: %d)" % (page, cursor.rowcount))


def read_room_list_json(conn, version):
    cursor = conn.cursor()
    sql = "SELECT `page`, `data` FROM `list_json` WHERE `group`='room' AND `version`=%s"
    cursor.execute(sql, args=[str(version)])

    room_list = []
    for result in cursor.fetchall():
        room_list.append({
            "page": result[0],
            "data": result[1]
        })

    Util.print_white("读取【教室列表】解析数据 [%d] 页" % len(room_list))
    return room_list


# 多线程处理
def write_room_info(mysql_pool, task_data, cookies):
    conn = mysql_pool.connection()
    cursor = conn.cursor()

    sql = "SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED"
    cursor.execute(sql)

    rowcount = 0
    for time in range(3):
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
            Util.print_yellow("MySQL deadlock error. Retry [%d]" % (time + 1))
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
