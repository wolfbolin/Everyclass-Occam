# coding=utf-8
import os
import json
import Util
import Room


# def update_room(config):
#     # Mock task
#     task_list = [
#         {
#             "tid": 1,
#             "group": "room",
#             "model": "list",
#             "code": None,
#             "version": "2019-11-27",
#         },
#         {
#             "tid": 2,
#             "group": "room",
#             "model": "table",
#             "code": False,
#             "version": "2019-11-27",
#         }
#     ]
#
#     for task in task_list:
#         if task['model'] == "list":
#             update_room_list(config, task['version'])
#         elif task['model'] == "table":
#             update_room_table(config, task['version'], task["code"])


# def update_room_list(config, version):
#     pull_room_list(config, version)
#     parse_room_list(config, version)
#     write_room_list(config, version)


def write_room_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    room_list_json = Util.read_json_list_data(conn, "room", version)

    # 合并多页数据
    room_info_list = []
    room_page_count = []
    for room in room_list_json:
        room_page_count.append(int(room["page"]))
        room_info_list.extend(json.loads(room["data"]))
    if len(room_page_count) != max(room_page_count):
        Util.print_yellow("【教室列表】页码与页数不相符，可能出现页面缺漏。count：%d，page：%d"
                          % (len(room_page_count), max(room_page_count)))

    Util.print_blue("插入【教室】基础数据 [%s] 条" % len(room_info_list))
    comm_data = {"version": str(version)}
    manager_list = Util.turbo_multiprocess(config, Room.write_room_info, comm_data, room_info_list,
                                           max_core=4, max_thread=8, mysql_config=config["mysql-entity"])
    Util.print_azure("插入【教室】基础数据 [%s] 条 (RC: %d)" % (len(room_info_list), sum(manager_list)))


# def update_room_table(config, version, code_list):
#     if code_list is False:
#         conn = Util.mysql_conn(config, "mysql-entity")
#         room_info_data = read_room_info(conn, None)
#         print(room_info_data)
#
#     pull_room_table(config, version)
#     parse_room_table(config, version)
#     write_room_table(config, version)


if __name__ == '__main__':
    _config = Util.get_config("../config")
    write_room_list(_config, "2019-11-27")
    # update_room_table(_config, "2019-11-27", False)
