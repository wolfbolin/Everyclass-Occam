# coding=utf-8
import json
import Util
import Config
import pymysql

week_sql_str = ",".join(['`week%s`' % i for i in range(1, 21)])  # `week1`,`week2`,`week3`...


def available_room(config, semester):
    conn = Util.mysql_conn(config, "mysql-entity")

    # 清空表数据
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE `avl_room`")

    # 更新教学楼与校区列表
    update_room_itemize(conn)

    # 更新空教室
    lesson_list = read_all_lesson(conn, semester)
    for i, lesson in enumerate(lesson_list):
        Util.process_bar(i + 1, len(lesson_list), "【教室信息】更新活动教室  ")
        update_active_room(conn, lesson)


def update_room_itemize(conn):
    cursor = conn.cursor()
    sql = "SELECT DISTINCT `campus`,`building`,`code`,`name` FROM `room`"
    cursor.execute(sql)
    room_group = {}
    for item in cursor.fetchall():
        room_group.setdefault(item[0], {})
        room_group[item[0]].setdefault(item[1], {})
        room_group[item[0]][item[1]].setdefault(item[2], item[3])
    sql = "REPLACE INTO `kvdb`(`key`, `val`) VALUES ('room_group', %s)"
    cursor.execute(sql, json.dumps(room_group, ensure_ascii=False))
    conn.commit()


def update_building_list(conn):
    cursor = conn.cursor()
    sql = "SELECT DISTINCT `building` FROM `room`"
    cursor.execute(sql)
    campus_list = [i[0] for i in cursor.fetchall()]
    sql = "REPLACE INTO `kvdb`(`key`, `val`) VALUES ('building_list', %s)"
    cursor.execute(sql, json.dumps(campus_list, ensure_ascii=False))
    conn.commit()


def read_all_lesson(conn, semester):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `code`,`session`,`week`,`room_code`,`room_name`,`course_code`,`course_name` " \
          "FROM `lesson` WHERE `semester`=%s"
    cursor.execute(sql, args=[semester])
    return cursor.fetchall()


def update_active_room(conn, lesson):
    if lesson["room_code"] == "":
        return
    week_list = json.loads(lesson["week"])
    sql = "INSERT INTO `avl_room`(`code`,`name`,`session`,%s) VALUES " % week_sql_str
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
    available_room(_config, "2020-2021-1")
