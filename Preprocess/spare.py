# coding=utf-8
import json
import Util
import Config
import pymysql

week_sql_str = ",".join(['`week%s`' % i for i in range(1, 21)])  # `week1`,`week2`,`week3`...


def spare_data(config, semester):
    conn = Util.mysql_conn(config, "mysql-entity")

    # TODO 清空现有表数据

    lesson_list = read_all_lesson(conn, semester)
    for i, lesson in enumerate(lesson_list):
        Util.process_bar(i + 1, len(lesson_list), "【教室信息】更新空教室  ")
        update_spare_room(conn, lesson)


def read_all_lesson(conn, semester):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `code`,`session`,`week`,`room_code`,`room_name`,`course_code`,`course_name` " \
          "FROM `lesson` WHERE `semester`=%s"
    cursor.execute(sql, args=[semester])
    return cursor.fetchall()


def update_spare_room(conn, lesson):
    if lesson["room_code"] == "":
        return
    week_list = json.loads(lesson["week"])
    sql = "INSERT INTO `spare`(`code`,`name`,`session`,%s) VALUES " % week_sql_str
    sql += "(%s) " % (",".join(["%s" for i in range(23)]))
    sql += "ON DUPLICATE KEY UPDATE `code`=`code`"
    base_args = [lesson["room_code"], lesson["room_name"], lesson["session"]]
    insert_args = []
    update_args = []
    for week in range(1, 21):
        if week in week_list:
            data = {
                "lesson": lesson["code"],
                "course_code": lesson["course_code"],
                "course_name": lesson["course_name"],
            }
            course_data = json.dumps(data, ensure_ascii=False)
            insert_args.append(course_data)
            sql += ",`week{}`=%s".format(week)
            update_args.append(course_data)
        else:
            insert_args.append("")

    cursor = conn.cursor()
    cursor.execute(sql, args=base_args + insert_args + update_args)
    conn.commit()


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    spare_data(_config, "2019-2020-2")
