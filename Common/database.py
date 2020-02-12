# coding=utf-8
import Util
import Config


# 写入列表数据
def write_html_data(conn, group, version, mark, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `html_bin` (`time`, `data`, `mark`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), str(mark), group, str(version)])
    conn.commit()
    return cursor.rowcount


# 删除列表数据
def delete_html_data(conn, group, version, mark):
    cursor = conn.cursor()
    sql = "DELETE FROM `html_bin` WHERE `group`=%s AND `version`=%s AND `mark`=%s"
    cursor.execute(sql, args=[group, version, mark])
    conn.commit()
    return cursor.rowcount


# 读取列表数据
def read_html_data(conn, group, version):
    cursor = conn.cursor()
    sql = "SELECT `mark`, `data` FROM `html_bin` WHERE `group`=%s AND `version`=%s"
    cursor.execute(sql, args=[str(group), str(version)])

    item_list = []
    for result in cursor.fetchall():
        item_list.append({
            "mark": result[0],
            "data": result[1]
        })

    return item_list


# 写入格式化数据
def write_json_data(conn, group, version, mark, data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `json_bin` (`time`, `data`, `mark`, `group`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[Util.str_time(), str(data), str(mark), group, str(version)])
    conn.commit()


# 删除列表数据
def delete_json_data(conn, group, version, mark):
    cursor = conn.cursor()
    sql = "DELETE FROM `json_html` WHERE `group`=%s AND `version`=%s AND `mark`=%s"
    cursor.execute(sql, args=[group, version, mark])
    conn.commit()
    return cursor.rowcount


# 读取格式化数据
def read_json_data(conn, group, version):
    cursor = conn.cursor()
    sql = "SELECT `mark`, `data` FROM `json_bin` WHERE `group`=%s AND `version`=%s"
    cursor.execute(sql, args=[str(group), str(version)])

    item_list = []
    for result in cursor.fetchall():
        item_list.append({
            "mark": result[0],
            "data": result[1]
        })

    return item_list


# 读取已完成的页面
def read_exist_html_data(config, version, task_key):
    conn = Util.mysql_conn(config, "mysql-occam")
    json_list = read_html_data(conn, task_key[1], version)
    exist_page_mark = list()
    for page in json_list:
        exist_page_mark.append(page["mark"])
    Util.print_white("【%s】读取已完成%s页" % (task_key[0], len(json_list)))
    return json_list, exist_page_mark


# 读取已完成的数据
def read_exist_json_data(config, version, task_key):
    conn = Util.mysql_conn(config, "mysql-occam")
    json_list = read_json_data(conn, task_key[1], version)
    exist_page_mark = list()
    for page in json_list:
        exist_page_mark.append(page["mark"])
    Util.print_white("【%s】读取已完成%s页" % (task_key[0], len(json_list)))
    return json_list, exist_page_mark


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    _conn = Util.mysql_conn(_config, "mysql-occam")
    print(read_html_data(_conn, "student", "2019-11-27"))
