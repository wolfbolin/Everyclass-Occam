# coding=utf-8
import os
from .spider import *


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
