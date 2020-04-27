# coding=utf-8
import gc
import re
import time
import json
import Util
import Config
import Common
from math import ceil
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

lesson_translation_table = {
    "课程名称": "name_str",
    "老师": "teacher_str",
    "教学班名称": "class_str",
    "行政班级名称": "class_str",
    "选课人数": "pick_str",
    "周次": "week_str",
    "单双周": "loop_str",
    "节次": "session_str",
    "上课地点教室": "room_str",
    "课程类别": "category_str",
    "课程性质": "nature_str",
    "上课总学时": "tea_hour_str",
}


def fetch_class_table(config, version, task_name, task_word, task_group, url_index, semester, active_list):
    # 预处理参数
    task_key = (task_name, task_word, task_group)
    headers, cookies = Common.auth_cookie(config)
    occam_conn = Util.mysql_conn(config, "mysql-occam")

    # 读取缓存数据
    cache_data, exist_mark = Common.read_exist_html_data(config, version, task_key)
    if len(exist_mark) == len(active_list):
        Util.print_azure("该版本【%s】无需下载更新" % task_name)

    # 获取课表信息
    for i, obj_data in enumerate(active_list):
        time_start = time.time()
        extra_data = Util.dict_link(config[task_key[2] + "_info"], obj_data)

        # 尝试获取页面
        Util.print_white("【%s】(%s/%s)" % (task_key[0], i + 1, len(active_list)), end='')
        if extra_data["code"] in exist_mark:
            Util.print_white("重新计算 <%s:%s> 课表..." % (semester, extra_data["name"]), end='')
            cache = cache_data[exist_mark.index(extra_data["code"])]
            http_result = cache["data"]
        else:
            Util.print_white("正在下载 <%s:%s> 课表..." % (semester, extra_data["name"]), end='')
            obj_data["semester"] = semester
            http_result = pull_table_page(config, version, task_key, url_index, headers, obj_data)

        # 解析页面信息
        parse_list_page(config, occam_conn, version, task_key, http_result, obj_data)
        time_end = time.time()

        Util.print_green("OK", tag='', end='')
        Util.print_yellow("(%ss)" % ceil(time_end - time_start), tag='')


def fetch_class_table_oc(config, version, task_name, task_word, task_group, url_index, semester, active_list):
    # 预处理参数
    task_key = (task_name, task_word, task_group)
    headers, cookies = Common.auth_cookie(config)

    # 读取缓存数据
    cache_data, exist_mark = Common.read_exist_html_data(config, version, task_key)
    if len(exist_mark) == len(active_list):
        Util.print_azure("该版本【%s】无需下载更新" % task_key[0])

    # 获取课表信息
    task_data = []
    for i, obj_data in enumerate(active_list):
        time_start = time.time()
        extra_data = Util.dict_link(config[task_key[2] + "_info"], obj_data)

        # 尝试获取页面
        Util.print_white("【%s】(%s/%s)" % (task_key[0], i + 1, len(active_list)), end='')
        if extra_data["code"] in exist_mark:
            Util.print_white("重新计算 <%s:%s:%s> 课表..." % (semester, task_key[2], extra_data["name"]), end='')
            cache = cache_data[exist_mark.index(extra_data["code"])]
            http_result = cache["data"]
        else:
            Util.print_white("正在下载 <%s:%s:%s> 课表..." % (semester, task_key[2], extra_data["name"]), end='')
            obj_data["semester"] = semester
            http_result = pull_table_page(config, version, task_key, url_index, headers, obj_data)

        # 解析页面信息
        task_data.append({"http_result": http_result, "obj_data": obj_data})
        time_end = time.time()

        Util.print_green("OK", tag='', end='')
        Util.print_yellow("(%ss)" % ceil(time_end - time_start), tag='')
    del active_list
    gc.collect()

    # 解析课表信息
    Util.print_azure("即将批量解析【%s】" % task_key[0])
    comm_data = {
        "config": config,
        "version": version,
        "task_key": task_key

    }
    Util.turbo_multiprocess(config, parse_list_page_oc, comm_data, task_data,
                            db_list=["mysql-occam"], max_process=8, max_thread=4)


def parse_list_page_oc(mysql_pool, config, version, task_key, http_result, obj_data):
    conn = mysql_pool["mysql-occam"].connection()
    return parse_list_page(config, conn, version, task_key, http_result, obj_data)


def parse_list_page(config, conn, version, task_key, http_result, obj_data):
    extra_data = Util.dict_link(config[task_key[2] + "_info"], obj_data)

    # 解析页面数据
    lesson_list = []
    try:
        soup = BeautifulSoup(http_result, "lxml")
        table = soup.find("table")
        lines = table.find_all("tr")

        week_index = calc_week_column(lines[0])

        for line_index, line in enumerate(lines[1:6]):
            columns = line.find_all("td")
            for column_index, column in enumerate(columns[1:]):
                session = calc_session(line_index, week_index[column_index])

                lessons = column.find(class_="kbcontent").find_all("a")
                for lesson in lessons:
                    lesson_info = calc_lesson_tag(lesson["onclick"])
                    lesson_info["session"] = session

                    infos = lesson.find_all("font")
                    for info in infos:
                        key = lesson_translation_table[info["title"]]
                        lesson_info[key] = Util.purify_string(calc_purify_string(info))

                    lesson_list.append(lesson_info)

        remark = soup.find(id="bzdiv").string
        table_data = {
            "remark": remark,
            "lesson": lesson_list
        }
        # 写入已获取的数据
        table_data = json.dumps(table_data, ensure_ascii=False)
        Common.write_json_data(conn, task_key[1], version, extra_data["code"], table_data)
    except AttributeError as e:
        Util.write_log("pull_%s_data" % task_key[1], http_result)
        # Common.delete_html_data(conn, task_key[1], version, extra_data["code"])
        Util.print_red("【%s】编号 <%s> 解析失败，解析页面已写入日志，原数据已删除" % (task_key[0], extra_data["code"]))
        Util.print_red(e, tag="")


def pull_table_page(config, version, task_key, url_index, headers, obj_data):
    conn = Util.mysql_conn(config, "mysql-occam")

    url = config["url"][url_index]
    http_data = Util.dict_link(config[task_key[1] + "_data"], obj_data)
    extra_data = Util.dict_link(config[task_key[2] + "_info"], obj_data)
    http_result = Util.http_request("POST", url, headers=headers, data=http_data, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【%s】对象 <%s> 课表时，网络请求失败" % (task_key[0], extra_data["name"]))

    # 写入已获取的数据
    Common.write_html_data(conn, task_key[1], version, extra_data["code"], http_result)

    return http_result


def update_table_info(config, version, task_name, task_word, task_group, semester):
    task_key = (task_name, task_word, task_group)
    occam_conn = Util.mysql_conn(config, "mysql-occam")
    entity_conn = Util.mysql_conn(config, "mysql-entity")

    # 读取页面信息
    class_table_data = Common.read_json_data(occam_conn, task_key[1], version)

    # 删除已有的数据
    Util.print_blue("【%s】正在删除link&remark已有数据" % task_key[0])
    Common.delete_semester_data(entity_conn, "link", semester, task_key[2])
    Common.delete_semester_data(entity_conn, "remark", semester, task_key[2])

    # 写入课表信息
    for i, table_data in enumerate(class_table_data):
        obj_code = table_data["mark"]
        obj_data = json.loads(table_data["data"])
        Util.print_white("【%s】(%s/%s)" % (task_key[0], i + 1, len(class_table_data)), end='')
        Util.print_white("正在写入 <%s:%s:%s> 课表..." % (semester, task_key[2], obj_code))

        write_table_info(entity_conn, semester, task_key[2], obj_code, obj_data)


def update_table_info_oc(config, version, task_name, task_word, task_group, semester):
    task_key = (task_name, task_word, task_group)
    occam_conn = Util.mysql_conn(config, "mysql-occam")
    entity_conn = Util.mysql_conn(config, "mysql-entity")

    # 读取页面信息
    class_table_data = Common.read_json_data(occam_conn, task_key[1], version)
    task_data = [{"obj_code": x["mark"], "obj_data": json.loads(x["data"])} for x in class_table_data]

    # 删除已有的数据
    Util.print_blue("【%s】正在删除link & remark已有数据" % task_key[0])
    Common.delete_semester_data(entity_conn, "link", semester, task_key[2])
    Common.delete_semester_data(entity_conn, "remark", semester, task_key[2])

    # 写入课表信息
    Util.print_azure("即将批量写入【%s】" % task_key[0])
    comm_data = {
        "semester": semester,
        "group": task_key[2]
    }
    Util.turbo_multiprocess(config, write_table_info_oc, comm_data, task_data,
                            db_list=["mysql-entity"], max_process=8, max_thread=4)


def write_table_info_oc(mysql_pool, semester, group, obj_code, obj_data):
    conn = mysql_pool["mysql-entity"].connection()
    return write_table_info(conn, semester, group, obj_code, obj_data)


def write_table_info(conn, semester, group, obj_code, obj_data):
    for lesson in obj_data["lesson"]:
        week_str = lesson["week_str"]
        if "loop_str" in lesson.keys():
            week_str += "/" + lesson["loop_str"]
        week = read_week_string(week_str)

        lesson_info = {
            "code": lesson["jxid"],
            "week": json.dumps(week),
            "session": lesson["session"],
            "semester": semester,
        }
        Common.write_lesson_info(conn, lesson_info)

        lesson_link = {
            "lesson": lesson["jxid"],
            "session": lesson["session"],
            "object": obj_code,
            "group": group,
            "semester": semester,
        }
        Common.write_lesson_link(conn, lesson_link)

    if obj_data["remark"].strip() != "":
        remark_info = {
            "code": obj_code,
            "group": group,
            "remark": obj_data["remark"].strip(),
            "semester": semester,
        }
        Common.write_remark_info(conn, remark_info)


def calc_week_column(line):
    week_index = dict()
    columns = line.find_all("th")
    for index, column in enumerate(columns[1:]):
        week_index[index] = column.string
    return week_index


def calc_session(line_index, week_name):
    week_number = {
        "星期一": 1,
        "星期二": 2,
        "星期三": 3,
        "星期四": 4,
        "星期五": 5,
        "星期六": 6,
        "星期日": 7,
    }
    column_index = week_number[week_name]

    session = str(column_index)
    session += str(line_index * 2 + 1).zfill(2)
    session += str((line_index + 1) * 2).zfill(2)
    return session


def calc_lesson_tag(tag_str):
    res = re.search(r"jx0408id=(?P<jxid>\w+)&classroomID=(?P<rid>\w?)", tag_str)
    return res.groupdict()


def calc_purify_string(navigable_string):
    res = ""
    for string in navigable_string.stripped_strings:
        res += Util.purify_string(string)
    return str(res)


def read_week_string(week_str):
    # 排除双横杠的异常字符串 例如：4--5,7-18/全周
    week_str = week_str.replace('--', '-')
    length = week_str.split('/')[0]
    try:
        cycle = week_str.split('/')[1]
    except IndexError:
        cycle = 0

    if cycle == '单周' or cycle == '单':
        cycle = 1
    elif cycle == '双周' or cycle == '双':
        cycle = 2
    else:
        cycle = 0

    week = []
    try:
        for part in length.split(','):
            point = part.split('-')
            if len(point) == 1:  # 说明没有时间跨度
                if len(point[0]) == 0:
                    continue
                week.append(int(point[0]))
            else:  # 说明具有时间跨度
                for t in range(int(point[0]), int(point[1]) + 1):
                    if cycle == 0:
                        week.append(int(t))
                    elif cycle == 1 and t % 2 == 1:
                        week.append(int(t))
                    elif cycle == 2 and t % 2 == 0:
                        week.append(int(t))
    except ValueError:
        Util.print_red('奇怪的时间信息：{}'.format(week_str))
    week.sort()
    return week


if __name__ == '__main__':
    _config = Config.load_config("../Config")
    # _conn = Util.mysql_conn(_config, "mysql-occam")
    # _act_room_list = [{
    #     "jsid": "2420104",
    #     "jsmc": "世Ａ104"
    # }]
    # fetch_class_table(_config, "2019-11-27", "课表教室", "room_table", "jskb", "2019-2020-1", _act_room_list)
    # _task_key = ("课表教室", "room_table")
    # _test_html = Common.read_html_data(_conn, "room_table", "2019-11-27")
    # parse_list_page(_config, "2019-11-27", _task_key, _test_html[0]["data"],
    #                 {"jsid": "4080282", "jsmc": "S216"})
    # update_table_info(_config, "2019-11-27", "课表教室", "room_table", "room")
