# coding=utf-8
import re
import time
import json
import Util
import Config
import Common
from math import ceil
from bs4 import BeautifulSoup

lesson_translation_table = {
    "课程名称": "name_str",
    "老师": "teacher_str",
    "教学班名称": "class_str",
    "选课人数": "pick_str",
    "周次": "week_str",
    "单双周": "loop_str",
    "节次": "session_str",
    "上课地点教室": "room_str"
}


def fetch_class_schedule(config, version, task_name, task_word, url_index, semester, active_list):
    """
    批量更新课表信息数据
    :param config:
    :param version:
    :param task_name:
    :param task_word:
    :param url_index: 链接关键字
    :param semester:
    :param active_list:
    :return:
    """
    # 预处理参数
    task_key = (task_name, task_word)
    headers, cookies = Common.auth_cookie(config)

    # 读取缓存数据
    cache_data, exist_mark = Common.read_exist_data(config, version, task_key)
    if len(exist_mark) == len(active_list):
        Util.print_white("该版本【%s】无需下载更新" % task_name)

    # 获取课表信息
    for obj_data in active_list:
        extra_data = Util.dict_link(config[task_key[1] + "_extra"], obj_data)
        Util.print_white("【%s】正在下载 <%s> 课表..." % (task_name, extra_data["name"]), end='')

        # 尝试获取页面
        time_start = time.time()
        obj_data["semester"] = semester
        http_result = pull_table_page(config, version, task_key, url_index, headers, obj_data)

        # 解析页面信息
        parse_list_page(config, version, task_key, http_result, obj_data)
        time_end = time.time()

        Util.print_green("OK", tag='', end='')
        Util.print_yellow("(%ss)" % ceil(time_end - time_start), tag='')


def pull_table_page(config, version, task_key, url_index, headers, obj_data, ):
    conn = Util.mysql_conn(config, "mysql-occam")

    url = config["url"][url_index]
    http_data = Util.dict_link(config[task_key[1] + "_data"], obj_data)
    extra_data = Util.dict_link(config[task_key[1] + "_extra"], obj_data)
    http_result = Util.http_request("POST", url, headers=headers, data=http_data, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【%s】对象 <%s> 课表时，网络请求失败" % (task_key[0], extra_data["name"]))

    # 写入已获取的数据
    Common.write_html_data(conn, task_key[1], version, extra_data["code"], http_result)

    return http_result


def parse_list_page(config, version, task_key, http_result, obj_data):
    conn = Util.mysql_conn(config, "mysql-occam")
    extra_data = Util.dict_link(config[task_key[1] + "_extra"], obj_data)

    # 解析页面数据
    lesson_list = []
    try:
        soup = BeautifulSoup(http_result, "lxml")
        table = soup.find("table")
        lines = table.find_all("tr")
        for line_index, line in enumerate(lines[1:6]):
            columns = line.find_all("td")
            for column_index, column in enumerate(columns[1:]):
                session = calc_session(line_index, column_index)

                lessons = column.find(class_="kbcontent").find_all("a")
                for lesson in lessons:
                    lesson_info = calc_lesson_tag(lesson["onclick"])
                    lesson_info["session"] = session

                    infos = lesson.find_all("font")
                    for info in infos:
                        key = lesson_translation_table[info["title"]]
                        lesson_info[key] = Util.purify_string(calc_purify_string(info))

                    lesson_list.append(lesson_info)

        # 写入已获取的数据
        lesson_list = json.dumps(lesson_list, ensure_ascii=False)
        Common.write_json_data(conn, task_key[1], version, extra_data["code"], lesson_list)
    except AttributeError as e:
        Util.write_log("pull_%s_data" % task_key[1], http_result)
        # Common.delete_html_data(conn, task_key[1], version, extra_data["code"])
        Util.print_red("【%s】编号 <%s> 解析失败，解析页面已写入日志，原数据已删除" % (task_key[0], extra_data["code"]))
        Util.print_red(e, tag="")


def calc_session(line_index, column_index):
    session = str(column_index + 1)
    session += str(line_index * 2 + 1).zfill(2)
    session += str((line_index + 1) * 2).zfill(2)
    return session


def calc_lesson_tag(tag_str):
    res = re.search(r"jx0408id=(?P<jxid>\w+)&classroomID=(?P<rid>\w+)", tag_str)
    return res.groupdict()


def calc_purify_string(navigable_string):
    res = ""
    for string in navigable_string.stripped_strings:
        res += Util.purify_string(string)
    return str(res)


if __name__ == '__main__':
    _config = Config.load_config("../Config")
    _conn = Util.mysql_conn(_config, "mysql-occam")
    # _act_room_list = Common.read_json_data(_conn, "act_room", "2019-11-27")
    # _act_room_list = json.loads(_act_room_list[0]["data"])
    # fetch_schedule_card(_config, "2019-11-27", "课表教室", "room_table", "jskb", "2019-2020-1", _act_room_list)
    # _task_key = ("课表教室", "room_table")
    # _test_html = Common.read_html_data(_conn, "room_table", "2019-11-27")
    # parse_list_page(_config, "2019-11-27", _task_key, _test_html[0]["data"],
    #                 {"jsid": "4080282", "jsmc": "S216"})
