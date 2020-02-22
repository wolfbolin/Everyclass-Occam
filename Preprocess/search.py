# coding=utf-8
import re
import json
import Util
import Config
import pymysql
import pypinyin


def preprocess_search_data(config):
    # 读取改名规则
    rename_rule = read_rename_rule(config)

    # 更新教室搜索数据
    recalculation_search_key(config, rename_rule, "room", ["campus", "building"])

    # 更新课程搜索数据
    recalculation_search_key(config, rename_rule, "course", ["type", "faculty"])

    # 更新教师搜索数据
    recalculation_search_key(config, rename_rule, "teacher", ["title", "department"])

    # 更新学生搜索数据
    recalculation_search_key(config, rename_rule, "student", ["class", "department"])


def recalculation_search_key(config, rename_rule, group, params):
    conn = Util.mysql_conn(config, "mysql-entity")
    base_info = read_object_base(conn, group, params)
    delete_search_group(conn, group)
    for i, info in enumerate(base_info):
        Util.print_white("【搜索处理】(%s/%s)" % (i + 1, len(base_info)), end="")
        Util.print_white("正在写入 <%s:%s:%s> 搜索数据..." % (group, info["name"], info["code"]))

        # 计算名称改写与拼音
        name_list = convert_search_name(rename_rule, info["name"])
        name_list = convert_pinyin_name(name_list)

        # 计算对象可用学期
        semester_list = read_available_semester(conn, group, info["code"])
        semester_list = json.dumps(semester_list)

        for name in name_list:
            write_search_key(conn, group, name, info["code"], info["name"],
                             info[params[0]], info[params[1]], semester_list)


def convert_search_name(rename_rule, name):
    name_list = [name]
    for rule in rename_rule:
        new_name = re.sub(rule["regex"], rule["entitle"], name)
        if new_name == name:
            continue
        name_list.append(new_name)
    return name_list


def convert_pinyin_name(name_list):
    pinyin_name = set()
    for name in name_list:
        full_pinyin = pypinyin.pinyin(name, errors='ignore', style=pypinyin.Style.NORMAL)
        full_pinyin = ''.join(list(x[0] for x in full_pinyin)).strip()
        if len(full_pinyin) > 1:
            pinyin_name.add(full_pinyin)
        first_pinyin = pypinyin.pinyin(name, errors='ignore', style=pypinyin.Style.FIRST_LETTER)
        first_pinyin = ''.join(list(x[0] for x in first_pinyin)).strip()
        if len(full_pinyin) > 1:
            pinyin_name.add(first_pinyin)
    return list(pinyin_name)


def read_rename_rule(config):
    conn = Util.mysql_conn(config, "mysql-occam")
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT * FROM `rename`"
    cursor.execute(sql)
    return cursor.fetchall()


def read_object_base(conn, table, key):
    key.extend(["name", "code"])
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `%s` FROM `%s`" % ("`,`".join(key), table)
    cursor.execute(sql)
    return cursor.fetchall()


def write_search_key(conn, group, key, code, name, info1, info2, semester):
    cursor = conn.cursor()
    sql = "REPLACE INTO `search`(`key`,`code`,`name`,`group`,`info1`,`info2`,`semester`) " \
          "VALUES(%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql, args=[key, code, name, group, info1, info2, semester])
    conn.commit()


def delete_search_group(conn, group):
    cursor = conn.cursor()
    sql = "DELETE FROM `search` WHERE `group`=%s"
    cursor.execute(sql, args=[group])
    conn.commit()


def read_available_semester(conn, group, code):
    cursor = conn.cursor()
    sql = "SELECT DISTINCT `semester` FROM `link` WHERE `object`=%s AND `group`=%s"
    cursor.execute(sql, args=[code, group])
    return [obj[0] for obj in cursor.fetchall()]


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    preprocess_search_data(_config)
