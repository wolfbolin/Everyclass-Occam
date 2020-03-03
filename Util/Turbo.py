# coding=utf-8
import os
import Util
import time
import json
import queue
import pymysql
import multiprocessing
from inspect import isfunction
from DBUtils.PooledDB import PooledDB
from concurrent.futures import ThreadPoolExecutor, as_completed, wait


class DataIterator:
    def __init__(self, task_func, task_queue, data_queue, mysql_pool):
        self.task_func = task_func
        self.task_queue = task_queue
        self.data_queue = data_queue
        self.mysql_pool = mysql_pool

    def __iter__(self):
        return self

    def __next__(self):
        task_data = self.task_queue.get()
        if isinstance(task_data, Util.ExitSignal):
            raise StopIteration
        self.data_queue.put(task_data)
        return self.task_func, self.mysql_pool, self.data_queue


def turbo_multiprocess(config, task_func, comm_data, task_data, db_list=None, max_process=32, max_thread=64):
    # 类型校验
    if not isfunction(task_func):
        raise ValueError("[task_func] type error")
    if not isinstance(comm_data, dict):
        raise ValueError("[comm_data] type error")
    if not isinstance(task_data, list):
        raise ValueError("[task_data] type error")
    if not isinstance(max_process, int):
        raise ValueError("[max_process] type error")
    if not isinstance(max_thread, int):
        raise ValueError("[max_thread] type error")

    # 池化参数
    process_bin = []
    result_data = []
    core_num = min(Util.cpu_core(), max_process)
    result_list = multiprocessing.Manager().list()
    task_queue = multiprocessing.Queue(maxsize=max_process * max_thread)

    # 创建进程
    for i in range(core_num):
        process_arg = (config, task_func, task_queue, result_list, db_list, max_thread)
        process = multiprocessing.Process(target=multithread_master, args=process_arg)
        process.start()
        process_bin.append(process)

    # 等待进程创建
    time.sleep(1)
    Util.print_purple("进程创建成功，即将下发 [%d] 条数据" % len(task_data))

    # 下发任务数据
    for num, data in enumerate(task_data):
        data.update(comm_data)
        task_queue.put(data)
        Util.process_bar(num + 1, len(task_data), "任务下发量")

    # 下发终止指令
    for i in range(core_num):
        task_queue.put(Util.ExitSignal("Done"))

    # 等待进程结束
    for process in process_bin:
        process.join()

    # 收集计算产物
    for message in result_list:
        result_data.append(message)

    return result_data


def multithread_master(config, task_func, task_queue, result_list, db_list=None, max_thread=4):
    Util.print_yellow("Process start: [%5d]" % os.getpid())

    # 建立连接池
    mysql_pool = {}
    if mysql_pool is not None:
        for db_key in db_list:
            mysql_pool[db_key] = Util.mysql_pool(config, db_key)

    # 建立线程池
    data_queue = queue.Queue(maxsize=max_thread)
    executor = ThreadPoolExecutor(max_workers=max_thread)
    data_iter = DataIterator(task_func, task_queue, data_queue, mysql_pool)

    # 动态分配任务并收集结果
    for res in executor.map(multithread_slave, data_iter):
        result_list.append(res)


def multithread_slave(data_pack):
    task_func, mysql_pool, data_queue = data_pack
    task_data = data_queue.get()
    task_func(mysql_pool, **task_data)


if __name__ == "__main__":
    pass
