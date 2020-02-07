# coding=utf-8
import Util
import Config


# 写入列表数据
def write_html_list_data(conn, group, version, page, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `list_html` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), group, str(version)])
    conn.commit()
    return cursor.rowcount


# 删除列表数据
def delete_html_list_data(conn, group, version, page):
    cursor = conn.cursor()
    sql = "DELETE FROM `list_html` WHERE `group`=%s AND `version`=%s AND `page`=%s"
    cursor.execute(sql, args=[group, version, page])
    conn.commit()
    return cursor.rowcount


# 读取列表数据
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


# 写入格式化数据
def write_json_list_data(conn, group, version, page, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `list_json` (`time`, `data`, `page`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), int(page), group, str(version)])
    conn.commit()


# 删除列表数据
def delete_json_list_data(conn, group, version, page):
    cursor = conn.cursor()
    sql = "DELETE FROM `json_html` WHERE `group`=%s AND `version`=%s AND `page`=%s"
    cursor.execute(sql, args=[group, version, page])
    conn.commit()
    return cursor.rowcount


# 读取格式化数据
def read_json_list_data(conn, group, version):
    cursor = conn.cursor()
    sql = "SELECT `page`, `data` FROM `list_json` WHERE `group`=%s AND `version`=%s"
    cursor.execute(sql, args=[str(group), str(version)])

    item_list = []
    for result in cursor.fetchall():
        item_list.append({
            "page": result[0],
            "data": result[1]
        })

    return item_list


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    _conn = Util.mysql_conn(_config, "mysql-occam")
    print(read_html_list_data(_conn, "student", "2019-11-27"))
