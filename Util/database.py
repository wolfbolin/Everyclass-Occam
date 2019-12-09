# coding=utf-8
import Util
import pymysql


def read_html_list_data(conn, group, version):
    cursor = conn.cursor()
    sql = "SELECT `page`, `data` FROM `list_html` WHERE `group`=%s AND `version`=%s"
    cursor.execute(sql, args=[str(group), str(version)])

    item_list = []
    for result in cursor.fetchall():
        item_list.append({
            "page": result[0],
            "data": result[1]
        })

    return item_list


def write_html_list_data(conn, group, version, page, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `list_html` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), group, str(version)])
    conn.commit()

    return cursor.rowcount


def delete_html_list_data(conn, group, version, page):
    cursor = conn.cursor()
    sql = "DELETE FROM `list_html` WHERE `group`=%s AND `version`=%s AND `page`=%s"
    cursor.execute(sql, args=[group, version, page])
    conn.commit()

    return cursor.rowcount


def write_json_list_data(conn, group, version, page, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `list_json` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), group, str(version)])
    conn.commit()


if __name__ == "__main__":
    _config = Util.get_config("../config")
    _conn = Util.mysql_conn(_config, "mysql-occam")

    print(read_html_list_data(_conn, "student", "2019-11-27"))
