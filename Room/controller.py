# coding=utf-8
import os
import json
import Util
from Room.spider import *


def update_room(config):
    # Mock task
    task_list = [{
        "tid": 1,
        "group": "room",
        "model": "list",
        "code": None,
        "version": "2019-12-04",
    }]

    for task in task_list:
        if task['model'] == "list":
            update_room_list(config, task['version'])


def update_room_list(config, version):
    pull_room_list(config, version)
    parse_room_list(config, version)
    write_room_list(config, version)


def write_room_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    room_list_json = read_room_list_json(conn, version)

    # 合并多页数据
    room_info_list = []
    for room in room_list_json:
        room_info_list.extend(json.loads(room["data"]))

    # 写入实体集合
    # conn = Util.mysql_conn(config, "mysql-entity")
    # for room_info in room_info_list:
    #     write_room_info(conn, version, room_info)

    # Util.write_log("room_info_list", json.dumps(room_info_list))

    comm_data = {
        "version": str(version)
    }
    Util.turbo_multiprocess(config, write_room_info, comm_data, room_info_list,
                            max_thread=4, mysql_config=config["mysql-entity"])


if __name__ == '__main__':
    # 测试教室课表引入
    _config = Util.get_config("../config")
    write_room_list(_config, Util.str_time("2019-11-27"))
