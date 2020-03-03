# coding=utf-8
import json
import Util
import Config
import pymysql


def lesson_data(config, semester):
    conn = Util.mysql_conn(config, "mysql-entity")
    lesson_list = read_all_lesson(conn, semester)
    for i, lesson in enumerate(lesson_list):
        Util.process_bar(i + 1, len(lesson_list), "【课程卡片】更新信息  ")
        update_lesson_data(conn, lesson, semester)


def lesson_data_oc(config, semester):
    conn = Util.mysql_conn(config, "mysql-entity")
    lesson_list = read_all_lesson(conn, semester)
    task_data = [{"lesson": x} for x in lesson_list]

    Util.print_azure("即将批量更新【课程卡片】")
    comm_data = {
        "semester": semester
    }
    Util.turbo_multiprocess(config, update_lesson_data_oc, comm_data, task_data,
                            db_list=["mysql-entity"], max_process=8, max_thread=4)


def update_lesson_data_oc(mysql_pool, lesson, semester):
    conn = mysql_pool["mysql-entity"].connection()
    return update_lesson_data(conn, lesson, semester)


def update_lesson_data(conn, lesson, semester):
    room_info, course_info, teacher_info = read_lesson_info(conn, lesson["code"], lesson["session"], semester)
    lesson["week_str"] = make_week_string(json.loads(lesson["week"]))
    if room_info is None:
        lesson["room_code"] = ""
        lesson["room_name"] = ""
    else:
        lesson["room_code"] = room_info["code"]
        lesson["room_name"] = room_info["name"]
    if course_info is None:
        lesson["course_code"] = ""
        lesson["course_name"] = ""
    else:
        lesson["course_code"] = course_info["code"]
        lesson["course_name"] = course_info["name"]
    if teacher_info is None:
        lesson["teacher_list"] = "[]"
    else:
        lesson["teacher_list"] = json.dumps(teacher_info, ensure_ascii=False)
    update_lesson_info(conn, lesson["code"], lesson["session"], semester, lesson)


def read_all_lesson(conn, semester):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT `code`,`session`,`week` FROM `lesson` WHERE `semester`=%s"
    cursor.execute(sql, args=[semester])
    return cursor.fetchall()


def read_lesson_info(conn, lesson, session, semester):
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 查询教室信息
    sql = "SELECT `code`,`name` FROM `link`,`room` WHERE `object`=`code` " \
          "AND `lesson`=%s AND `session`=%s AND `semester`=%s AND `group`='room'"
    cursor.execute(sql, args=[lesson, session, semester])
    room_info = cursor.fetchone()

    # 查询课程信息
    sql = "SELECT `code`,`name` FROM `link`,`course` WHERE `object`=`code` " \
          "AND `lesson`=%s AND `session`=%s AND `semester`=%s AND `group`='course'"
    cursor.execute(sql, args=[lesson, session, semester])
    course_info = cursor.fetchone()

    # 查询老师信息
    sql = "SELECT `code`,`name`,`title`,`department` FROM `link`,`teacher` WHERE `object`=`code` " \
          "AND `lesson`=%s AND `session`=%s AND `semester`=%s AND `group`='teacher'"
    cursor.execute(sql, args=[lesson, session, semester])
    teacher_info = cursor.fetchall()

    return room_info, course_info, teacher_info


def update_lesson_info(conn, lesson, session, semester, data):
    cursor = conn.cursor()
    sql = "UPDATE `lesson` SET `week_str`=%s,`course_code`=%s,`course_name`=%s,`room_code`=%s,`room_name`=%s," \
          "`teacher_list`=%s WHERE `code`=%s AND `session`=%s AND `semester`=%s"
    cursor.execute(sql, args=[data["week_str"], data["course_code"], data["course_name"], data["room_code"],
                              data["room_name"], data["teacher_list"], lesson, session, semester])
    conn.commit()


def make_week_string(time_list):
    # 自带去重排序效果（仅增强健壮性，不可依赖）
    time_list = list(set(time_list))
    # 判断异常
    if len(time_list) == 0:
        Util.print_red('发现了没有周次的课程')
        return ""
    # 判断一周的课程
    if len(time_list) == 1:
        return '%d/全周' % time_list[0]
    # 判断单双全周
    dt = []
    for i in range(1, len(time_list)):
        dt.append(time_list[i] - time_list[i - 1])
    dt = list(set(dt))
    if len(dt) == 1:  # 说明周次是有规律的
        if dt[0] == 1:  # 说明是全周课程
            return '%d-%d/全周' % (time_list[0], time_list[-1])
        if dt[0] == 2 and time_list[0] % 2 == 1:  # 说明是单周
            return '%d-%d/单周' % (time_list[0], time_list[-1])
        if dt[0] == 2 and time_list[0] % 2 == 0:  # 说明是双周
            return '%d-%d/双周' % (time_list[0], time_list[-1])
    # 不能进行单双全周聚合的时间
    time_list.append(999)  # 添加不可能存在的周次推动最后一组数据进入结果
    begin = time_list[0]
    result = ''
    for i in range(1, len(time_list)):
        if time_list[i] != time_list[i - 1] + 1:  # 说明时间发生了不连续的情况
            if time_list[i - 1] == begin:
                result += ',%d' % time_list[i - 1]
            else:
                result += ',%d-%d' % (begin, time_list[i - 1])
            begin = time_list[i]
    return result[1:] + '/全周'


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    lesson_data(_config, "2019-2020-2")
