# coding=utf-8
import Util


def read_room_list(conn, version):
    cursor = conn.cursor()
    sql = "SELECT `page`, `data` FROM `list_html` WHERE `group`='room' AND `version`=%s"
    cursor.execute(sql, args=[version])

    room_list = []
    for result in cursor.fetchall():
        room_list.append({
            "page": result[0],
            "data": result[1]
        })

    Util.print_white("读取【教室列表】 [%d] 页" % len(room_list))
    return room_list


def write_room_list(conn, version, page, data):
    cursor = conn.cursor()
    sql = "INSERT INTO `list_html` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), "room", str(version)])
    conn.commit()

    Util.print_white("插入【教室列表】第[%s]页 (RC: %d)" % (page, cursor.rowcount))
