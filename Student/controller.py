# coding=utf-8
import os
import json
import Util
import Student


# def update_student(config):
#     # Mock task
#     task_list = [
#         {
#             "tid": 1,
#             "group": "student",
#             "model": "list",
#             "code": None,
#             "version": "2019-11-27",
#         },
#         {
#             "tid": 2,
#             "group": "student",
#             "model": "table",
#             "code": False,
#             "version": "2019-11-27",
#         }
#     ]
# 
#     for task in task_list:
#         if task['model'] == "list":
#             update_student_list(config, task['version'])
#         elif task['model'] == "table":
#             update_student_table(config, task['version'], task["code"])


def write_student_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    student_json_list = Util.read_json_list_data(conn, "student", version)

    # 合并多页数据
    student_info_list = []
    student_page_count = []
    for student in student_json_list:
        student_page_count.append(int(student["page"]))
        student_info_list.extend(json.loads(student["data"]))
    if len(student_page_count) != max(student_page_count):
        Util.print_yellow("【学生列表】页码与页数不相符，可能出现页面缺漏。count：%d，page：%d"
                          % (len(student_page_count), max(student_page_count)))

    Util.print_blue("插入【学生】基础数据 [%s] 条" % len(student_info_list))
    comm_data = {"version": str(version)}
    manager_list = Util.turbo_multiprocess(config, Student.write_student_info, comm_data, student_info_list,
                                           mysql_config=config["mysql-entity"])
    Util.print_azure("插入【学生】基础数据 [%s] 条 (RC: %d)" % (len(student_info_list), sum(manager_list)))


if __name__ == '__main__':
    _config = Util.get_config("../config")
    write_student_list(_config, "2019-11-27")
