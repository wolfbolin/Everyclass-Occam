# coding=utf-8
import re
import json
import Util
import Config
import pymysql
import pypinyin


def preprocess_search_data(config):
    occam_conn = Util.mysql_conn(config, "mysql-occam")
    entity_conn = Util.mysql_conn(config, "mysql-entity")
    # 读取改名规则
    rename_rule = read_rename_rule(occam_conn)

    # 更新课程搜索数据
    # course_base = read_object_base(config, "course", ["type", "faculty"])
    # delete_search_group(config, "course")
    # for i, course in enumerate(course_base):
    #     Util.print_white("【搜索课程】(%s/%s)" % (i + 1, len(course_base)), end="")
    #     Util.print_white("正在写入 <%s:%s> 课程搜索数据..." % (course["name"], course["code"]))
    #     name_list = convert_search_name(rename_rule, course["name"])
    #     for name in name_list:
    #         write_search_key(config, name, "course", course["code"])

    # 更新教室搜索数据
    room_base = read_object_base(entity_conn, "room", ["campus", "building"])
    delete_search_group(entity_conn, "room")
    for i, room in enumerate(room_base):
        Util.print_white("【搜索教室】(%s/%s)" % (i + 1, len(room_base)), end="")
        Util.print_white("正在写入 <%s:%s> 课程教室数据..." % (room["name"], room["code"]))
        name_list = convert_search_name(rename_rule, room["name"])
        semester_list = read_available_semester(entity_conn, "room", room["code"])
        semester_list = json.dumps(semester_list)
        for name in name_list:
            write_search_key(entity_conn, "room", name, room["code"],
                             room["campus"], room["building"], semester_list)

    # 更新教师搜索数据
    teacher_base = read_object_base(entity_conn, "teacher", ["title", "department"])
    delete_search_group(entity_conn, "teacher")
    for i, teacher in enumerate(teacher_base):
        Util.print_white("【搜索教师】(%s/%s)" % (i + 1, len(teacher_base)), end="")
        Util.print_white("正在写入 <%s:%s> 教师搜索数据..." % (teacher["name"], teacher["code"]))
        name_list = convert_pinyin_name([teacher["name"]])
        semester_list = read_available_semester(entity_conn, "teacher", teacher["code"])
        semester_list = json.dumps(semester_list)
        for name in name_list:
            write_search_key(entity_conn, "teacher", name, teacher["code"],
                             teacher["title"], teacher["department"], semester_list)

    # 更新学生搜索数据
    student_base = read_object_base(entity_conn, "student", ["class", "department"])
    delete_search_group(entity_conn, "student")
    for i, student in enumerate(student_base):
        Util.print_white("【搜索学生】(%s/%s)" % (i + 1, len(student_base)), end="")
        Util.print_white("正在写入 <%s:%s> 学生搜索数据..." % (student["name"], student["code"]))
        name_list = convert_pinyin_name([student["name"]])
        semester_list = read_available_semester(entity_conn, "student", student["code"])
        semester_list = json.dumps(semester_list)
        for name in name_list:
            write_search_key(entity_conn, "student", name, student["code"],
                             student["class"], student["department"], semester_list)


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


def read_rename_rule(conn):
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


def write_search_key(conn, group, key, code, info1, info2, semester):
    cursor = conn.cursor()
    sql = "REPLACE INTO `search`(`key`,`code`,`group`,`info1`,`info2`,`semester`) " \
          "VALUES(%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql, args=[key, code, group, info1, info2, semester])
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
