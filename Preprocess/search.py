# coding=utf-8
import re
import Util
import Config
import pymysql
import pypinyin


def preprocess_search_data(config):
    # 读取改名规则
    rename_rule = read_rename_rule(config)

    # 更新课程搜索数据
    course_base = read_object_base(config, "course")
    delete_search_group(config, "course")
    for i, course in enumerate(course_base):
        Util.print_white("【搜索课程】(%s/%s)" % (i + 1, len(course_base)), end="")
        Util.print_white("正在写入 <%s:%s> 课程搜索数据..." % (course["name"], course["code"]))
        name_list = convert_search_name(rename_rule, course["name"])
        for name in name_list:
            write_search_key(config, name, "course", course["code"])

    # 更新教室搜索数据
    room_base = read_object_base(config, "room")
    delete_search_group(config, "room")
    for i, room in enumerate(room_base):
        Util.print_white("【搜索教室】(%s/%s)" % (i + 1, len(room_base)), end="")
        Util.print_white("正在写入 <%s:%s> 课程教室数据..." % (room["name"], room["code"]))
        name_list = convert_search_name(rename_rule, room["name"])
        for name in name_list:
            write_search_key(config, name, "room", room["code"])

    # 更新学生搜索数据
    teacher_base = read_object_base(config, "teacher")
    delete_search_group(config, "teacher")
    for i, teacher in enumerate(teacher_base):
        Util.print_white("【搜索教师】(%s/%s)" % (i + 1, len(teacher_base)), end="")
        Util.print_white("正在写入 <%s:%s> 教师搜索数据..." % (teacher["name"], teacher["code"]))
        name_list = convert_pinyin_name([teacher["name"]])
        for name in name_list:
            write_search_key(config, name, "teacher", teacher["code"])

    # 更新学生搜索数据
    student_base = read_object_base(config, "student")
    delete_search_group(config, "student")
    for i, student in enumerate(student_base):
        Util.print_white("【搜索学生】(%s/%s)" % (i + 1, len(student_base)), end="")
        Util.print_white("正在写入 <%s:%s> 学生搜索数据..." % (student["name"], student["code"]))
        name_list = convert_pinyin_name([student["name"]])
        for name in name_list:
            write_search_key(config, name, "student", student["code"])


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


def read_object_base(config, table):
    conn = Util.mysql_conn(config, "mysql-entity")
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `code`,`name` FROM `%s`" % table
    cursor.execute(sql)
    return cursor.fetchall()


def write_search_key(config, key, group, code):
    conn = Util.mysql_conn(config, "mysql-entity")
    cursor = conn.cursor()
    sql = "REPLACE INTO `search`(`key`,`code`,`group`) VALUES(%s,%s,%s)"
    cursor.execute(sql, args=[key, code, group])
    conn.commit()


def delete_search_group(config, group):
    conn = Util.mysql_conn(config, "mysql-entity")
    cursor = conn.cursor()
    sql = "DELETE FROM `search` WHERE `group`=%s"
    cursor.execute(sql, args=[group])
    conn.commit()


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    preprocess_search_data(_config)
