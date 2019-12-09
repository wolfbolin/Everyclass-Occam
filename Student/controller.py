# coding=utf-8
import os
import json
import Util
from Student.spider import *


def update_student(config):
    # Mock task
    task_list = [
        {
            "tid": 1,
            "group": "student",
            "model": "list",
            "code": None,
            "version": "2019-11-27",
        },
        {
            "tid": 2,
            "group": "student",
            "model": "table",
            "code": False,
            "version": "2019-11-27",
        }
    ]

    for task in task_list:
        if task['model'] == "list":
            update_student_list(config, task['version'])
        elif task['model'] == "table":
            update_student_table(config, task['version'], task["code"])


def update_student_list(config, version):
    pull_student_list(config, version)
    parse_student_list(config, version)
    write_student_list(config, version)
