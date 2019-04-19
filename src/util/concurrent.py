# -*- coding: utf-8 -*-
# Common package
import json
import pymysql
from math import ceil
from DBUtils.PooledDB import PooledDB
from multiprocessing import Process, Manager
from concurrent.futures import ThreadPoolExecutor, as_completed
# Personal package
import util
import database


def multiprocess(task, main_data, attach_data=None, multithread=None, max_thread=5):
    """
    将大任务分配至4个核心完成，并在每个核心上使用多线程
    :param task: 完成单个任务的函数
    :param main_data: 数据数组，有差别数据
    :param attach_data: 数据字典，无差别数据
    :param multithread: 完成多线程的函数
    :param max_thread: 每个进程中的最大线程数
    """
    if multithread is None:
        return
    if attach_data is None:
        attach_data = {}
    data_length = len(main_data)
    manager = Manager()  # 单向向外传递信息
    manager_list = manager.list()
    # 进程任务分配
    slice1 = ceil(data_length / 4)
    slice2 = ceil(data_length / 2)
    slice3 = ceil(data_length / 4 * 3)
    process = [Process(target=multithread,
                       args=(task, main_data[0:slice1], attach_data, max_thread, manager_list)),
               Process(target=multithread,
                       args=(task, main_data[slice1:slice2], attach_data, max_thread, manager_list)),
               Process(target=multithread,
                       args=(task, main_data[slice2:slice3], attach_data, max_thread, manager_list)),
               Process(target=multithread,
                       args=(task, main_data[slice3:data_length], attach_data, max_thread, manager_list))]
    for p in process:
        p.start()
    for p in process:
        p.join()
    if isinstance(manager_list[0], int):
        return sum(manager_list)
    elif isinstance(manager_list[0], str):
        result = []
        result.extend(json.loads(manager_list[0]))
        result.extend(json.loads(manager_list[1]))
        result.extend(json.loads(manager_list[2]))
        result.extend(json.loads(manager_list[3]))
        return result
    else:
        return None


def mysql_multithread(task, main_data, attach_data, max_thread, manager_list,):
    """
    自动完成多线程的任务分配，利用多线程完成对于数据库的写入
    :param task: 完成单个任务的函数
    :param main_data: 数据数组，有差别数据
    :param attach_data: 数据字典，无差别数据
    :param max_thread: 每个进程中的最大线程数
    :param manager_list: 利用进程间共享队列回传数据
    :return 操作数据库行数
    """
    if attach_data is None:
        raise BaseException('未设定需要连接的数据库')
    executor = ThreadPoolExecutor(max_workers=max_thread)  # 建立线程池
    mysql_pool = PooledDB(creator=pymysql,
                          mincached=1, maxcached=max_thread,
                          maxconnections=max_thread,
                          host=util.mysql_host,
                          user=util.mysql_user,
                          passwd=util.mysql_password,
                          db=attach_data['mysql_database'],
                          port=util.mysql_port,
                          charset=util.mysql_charset,
                          setsession=['SET AUTOCOMMIT = 1'])  # 建立MySQL连接池
    all_work = []
    rowcount = 0
    progress = 0
    completed_work = 0
    quota = len(main_data)  # 每个任务只显示10次进度
    for data in main_data:
        if isinstance(data, dict) is False:
            # 输入的数据不是字典时进行数据格式转换
            data = {
                'main_data': data
            }
        if attach_data is not None:  # 添加无差异数据
            for key in attach_data:
                data[key] = attach_data[key]
        data['mysql_pool'] = mysql_pool  # 从连接池获取连接并添加到字典
        # 添加数据的操作可能会导致内存占用过多，待验证
        work = executor.submit(task, data)  # 向线程池提交任务
        all_work.append(work)  # 线程管理数组
    for work in as_completed(all_work):
        # 利用as_completed的阻塞效果完成信息的提取
        rowcount += work.result()
        completed_work += 1
        if ceil(completed_work / quota * 100) != progress:
            progress = ceil(completed_work / quota)
            util.process_bar(completed_work, quota, '完成%d项，修改%d行' % (completed_work, rowcount))
    manager_list.append(rowcount)  # return


def nosql_multithread(task, main_data, attach_data, max_thread, manager_list):
    """
    自动完成多线程的任务分配，利用多线程完成通用的多线程操作
    :param task: 完成单个任务的函数
    :param main_data: 数据数组，有差别数据
    :param attach_data: 数据字典，无差别数据
    :param max_thread: 每个进程中的最大线程数
    :param manager_list: 利用进程间共享队列回传数据
    :return 下载到的数据
    """
    executor = ThreadPoolExecutor(max_workers=max_thread)  # 建立线程池
    all_work = []
    result = []
    progress = 0
    completed_work = 0
    quota = len(main_data)  # 每个任务只显示10次进度
    for data in main_data:
        if isinstance(data, dict) is False:
            # 输入的数据不是字典时进行数据格式转换
            data = {
                'main_data': data
            }
        if attach_data is not None:  # 添加无差异数据
            for key in attach_data:
                data[key] = attach_data[key]
        # 添加数据的操作可能会导致内存占用过多，待验证
        work = executor.submit(task, data)  # 向线程池提交任务
        all_work.append(work)  # 线程管理数组
    for work in as_completed(all_work):
        # 利用as_completed的阻塞效果完成信息的提取
        work_result = work.result()
        if len(work_result) != 0:  # 过滤空的数据消息
            result.extend(work_result)
        completed_work += 1
        if ceil(completed_work / quota * 100) != progress:
            progress = ceil(completed_work / quota)
            util.process_bar(completed_work, quota, '完成%d项，还有%d项' % (completed_work, quota - completed_work))
    manager_list.append(json.dumps(result))  # return


def mongo_multithread(task, main_data, attach_data, max_thread, manager_list):
    """
    自动完成多线程的任务分配，利用多线程完成对于数据库的写入
    :param task: 完成单个任务的函数
    :param main_data: 数据数组，有差别数据
    :param attach_data: 数据字典，无差别数据
    :param max_thread: 每个进程中的最大线程数
    :param manager_list: 利用进程间共享队列回传数据
    :return 操作数据库行数
    """
    if attach_data is None:
        attach_data = {}
    executor = ThreadPoolExecutor(max_workers=max_thread)  # 建立线程池
    mongo_pool = database.mongo_connect()  # 建立MongoDB连接池
    all_work = []
    rowcount = 0
    progress = 0
    completed_work = 0
    quota = len(main_data)  # 每个任务只显示10次进度
    for data in main_data:
        if isinstance(data, dict) is False:
            # 输入的数据不是字典时进行数据格式转换
            data = {
                'main_data': data
            }
        if attach_data is not None:  # 添加无差异数据
            for key in attach_data:
                data[key] = attach_data[key]
        data['mongo_pool'] = mongo_pool  # 从连接池获取连接并添加到字典
        # 添加数据的操作可能会导致内存占用过多，待验证
        work = executor.submit(task, data)  # 向线程池提交任务
        all_work.append(work)  # 线程管理数组
    for work in as_completed(all_work):
        # 利用as_completed的阻塞效果完成信息的提取
        rowcount += work.result()
        completed_work += 1
        if ceil(completed_work / quota * 100) != progress:
            progress = ceil(completed_work / quota)
            util.process_bar(completed_work, quota, '完成%d项，修改%d行' % (completed_work, rowcount))
    manager_list.append(rowcount)  # return
