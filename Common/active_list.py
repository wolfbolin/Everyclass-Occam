# coding=utf-8
import re
import time
import json
import Util
import Config
import Common
from math import ceil


def fetch_active_list(config, version, task_name, task_word, url_index, semester):
    """
    获取指定学期可用的对象的列表
    :param config: 配置文件
    :param version: 版本信息
    :param task_name: 任务名称
    :param task_word: 任务关键字
    :param url_index: 链接关键字
    :param semester: 指定学期
    :return: 可用的对象列表
    """
    # 预处理参数
    task_key = (task_name, task_word)

    # 读取缓存数据
    cache_data, _ = Common.read_exist_json_data(config, version, task_key)
    if len(cache_data) != 0:
        Util.print_azure("该版本【%s】无需下载更新" % task_name)
        return json.loads(cache_data[0]["data"])

    # 获取指定页面
    headers, cookies = Common.auth_cookie(config)
    Util.print_white("【%s】正在下载..." % task_name, end='')
    time_start = time.time()
    http_result = pull_active_list_page(config, version, task_key, url_index, headers, semester)
    time_end = time.time()
    Util.print_green("OK", tag='', end='')
    Util.print_yellow("(%ss)" % ceil(time_end - time_start), tag='')

    # 解析页面信息
    active_list = parse_name_list(config, version, task_key, http_result)

    return active_list


def parse_name_list(config, version, task_key, http_result):
    conn = Util.mysql_conn(config, "mysql-occam")

    # 提取数据
    page_data = re.search(r'(var bj="\[|^\[)(.*?)("\];|\])', http_result, re.S | re.M)
    page_data = "[{}]".format(page_data.group(2))
    page_data = re.sub(r'\s', "", page_data)
    page_data = page_data.replace("'", '"')
    page_data = page_data.replace("\\", "\\\\")
    page_data = page_data.replace("]qz--1", "]")
    page_data = re.sub(r'([,|{])([\w]+)(:)', lambda x: '"'.join(x.groups()), page_data)
    page_data = json.loads(page_data)

    Common.write_json_data(conn, task_key[1], version, 1, json.dumps(page_data, ensure_ascii=False))
    Util.print_white("【%s】解析完成，共计%s个可用对象" % (task_key[0], len(page_data)))

    return page_data


def pull_active_list_page(config, version, task_key, url_index, headers, semester):
    conn = Util.mysql_conn(config, "mysql-occam")

    url = config["url"][url_index]
    if url_index == "jslb":
        params = {
            "method": "queryjs",
            "xnxq01id": semester
        }
    elif url_index == "jglb":
        params = {
            "method": "queryjg0101",
            "xnxq01id": semester
        }
    else:
        params = {
            "xnxq01id": str(semester),
            "isview": 1,
            "init": 1,
        }
    http_result = Util.http_request("POST", url, headers=headers, params=params, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【%s】时，网络请求失败" % task_key[0])

    # 写入已获取的数据
    Common.write_html_data(conn, task_key[1], version, 1, http_result)

    return http_result


def update_active_list(config, task_name, task_word, task_group, semester, active_list):
    # 预处理参数
    task_key = (task_name, task_word, task_group)
    conn = Util.mysql_conn(config, "mysql-entity")

    # 删除已有的学期数据
    Common.delete_semester_data(conn, "semester", semester, task_key[2])

    # 插入可用学期信息
    for i, obj_data in enumerate(active_list):
        base_info = Util.dict_link(config[task_key[2] + "_info"], obj_data)
        Common.write_active_semester(conn, base_info["code"], task_key[2], semester)
        Util.process_bar(i + 1, len(active_list), task_key[0])


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    fetch_active_list(_config, "2019-11-27", "可用教室", "act_room", "jslb", "2019-2020-1")
