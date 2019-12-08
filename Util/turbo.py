# coding=utf-8
import os
import Util
import json
import pymysql
import multiprocessing
from inspect import isfunction
from DBUtils.PooledDB import PooledDB
from concurrent.futures import ThreadPoolExecutor, as_completed


def turbo_multiprocess(config, task_func, comm_data, task_data, max_thread=4, mysql_config=None, add_cookies=False):
    # 类型校验
    if not isfunction(task_func):
        raise ValueError("[task_func] type error")
    if not isinstance(comm_data, dict):
        raise ValueError("[comm_data] type error")
    if not isinstance(task_data, list):
        raise ValueError("[task_data] type error")
    if not isinstance(max_thread, int):
        raise ValueError("[max_thread] type error")

    # 启动参数
    process_bin = []
    result_list = []
    core_num = Util.cpu_core()
    task_queue = multiprocessing.Queue()
    manager_list = multiprocessing.Manager().list()

    # 创建进程
    for i in range(core_num):
        process_arg = (config, task_func, task_queue, manager_list, max_thread, mysql_config, add_cookies)
        process = multiprocessing.Process(target=turbo_multithread, args=process_arg)
        process.start()
        process_bin.append(process)

    # 下发任务数据
    for data in task_data:
        data.update(comm_data)
        task_queue.put(data)

    # 下发终止指令
    for i in range(core_num):
        task_queue.put(Util.ExitSignal("Done"))

    # 等待进程结束
    for process in process_bin:
        process.join()

    # 收集计算产物
    for message in manager_list:
        result_list.append(json.loads(message))

    return result_list


def turbo_multithread(config, task_func, task_queue, manager_list, max_thread=4, mysql_config=None, add_cookies=False):
    Util.print_yellow("Process start: [%5d]" % os.getpid())

    worker_list = []
    executor = ThreadPoolExecutor(max_workers=max_thread)

    if mysql_config is not None:
        mysql_config["port"] = int(mysql_config["port"])
        config["mysql_pool"]["mincached"] = int(config["mysql_pool"]["mincached"])
        config["mysql_pool"]["maxcached"] = int(config["mysql_pool"]["maxcached"])
        config["mysql_pool"]["maxconnections"] = int(config["mysql_pool"]["maxconnections"])
        mysql_pool = PooledDB(creator=pymysql, **mysql_config, **config["mysql_pool"])
    else:
        mysql_pool = None

    if add_cookies:
        cookies = Util.auth_cookie(config)
    else:
        cookies = None

    while True:
        task_data = task_queue.get()
        if isinstance(task_data, Util.ExitSignal):
            break

        if mysql_pool is not None:
            task_data["conn"] = mysql_pool

        if cookies is not None:
            task_data["cookies"] = cookies

        worker = executor.submit(task_func, task_data)
        worker_list.append(worker)

    for worker in as_completed(worker_list):
        manager_list.append(json.dumps(worker.result()))


def unit_test(task_data):
    if "conn" in task_data.keys():
        del (task_data["conn"])

    return {
        "status": "ok",
        "code": Util.random_code(),
        "data": task_data
    }


if __name__ == '__main__':
    _config = Util.get_config("../config")
    print(turbo_multiprocess(_config, unit_test, {"comm": "info"}, [{"no": "data1"}],
                             mysql_config=_config["mysql-entity"]))
