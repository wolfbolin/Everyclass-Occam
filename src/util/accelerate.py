# -*- coding: utf-8 -*-
# Common package
import json
import pymysql
from math import ceil
import multiprocessing
from DBUtils.PooledDB import PooledDB
from concurrent.futures import ThreadPoolExecutor, as_completed


# 将任务分配至多个核心完成，并在每个核心上使用多线程
def multiprocess(configs, task_target, thread_target, data_list, attach_data):
    if attach_data is None:
        attach_data = {}
    task_num = len(data_list)
    # 进程任务分配
    process_list = []
    msg_input, msg_output = multiprocessing.Pipe()
    data_input, data_output = multiprocessing.Pipe()
    for i in range(configs.CPU_CORE):
        process_args = dict(target=thread_target, args=[configs, task_target, attach_data, msg_input, data_output])
        process_list.append(multiprocessing.Process(**process_args))
        process_list[-1].start()

    print('done')

    for task_data in data_list:
        data_input.send(task_data)

    for i in range(configs.CPU_CORE):
        data_input.send(None)

    calc_result = []
    message = msg_output.recv()
    while process_alive(process_list):
        if message[0] == 'success':
            calc_result.extend(message[1])
        elif message[0] == 'finish':
            pass

    return calc_result


# 检查进程是否全部退出
def process_alive(process_list):
    for process in process_list:
        if process.is_alive():
            return True
    return False


# 朴素多线程函数
def simple_multithread(configs, task_target, attach_data, msg_input, data_output):
    executor = ThreadPoolExecutor(max_workers=configs.MAX_THREAD)

    # 接收任务并交付线程池
    all_thread = []
    task_data = data_output.recv()
    while task_data:
        thread = executor.submit(task_target, (task_data, attach_data))
        all_thread.append(thread)
        task_data = data_output.recv()
    for thread in as_completed(all_thread):
        thread_result = thread.result()
        msg_input.send(('success', thread_result))
