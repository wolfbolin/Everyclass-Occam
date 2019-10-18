# coding=utf-8
import os
import time
import util
import Config
import pymysql
import multiprocessing


def read_and_insert(config, data_pipe):
    conn = pymysql.connect(**config.OCCAM_CONFIG)
    cursor = conn.cursor()
    sql = "INSERT INTO `html`(`code`,`cluster`,`webpage`) VALUES (%s,%s,%s)"
    data = data_pipe.recv()
    while data:
        file = open(data[0], 'r', encoding='utf8')
        raw_data = file.read()
        cursor.execute(query=sql, args=[data[1], data[2], raw_data])
        conn.commit()
        data = data_pipe.recv()
    util.print_info("Process %s exit" % os.getpid())


def write_cluster(cluster_name, data_path):
    process_list = []
    pipe_input, pipe_output = multiprocessing.Pipe()
    for i in range(run_config.CPU_CORE):
        process_args = dict(target=read_and_insert, args=[run_config, pipe_output])
        process_list.append(multiprocessing.Process(**process_args))
        process_list[-1].start()

    # 教师课表簇导入
    student_cache = os.path.abspath("{}/{}".format(data_path, "teacher_html"))
    file_list = os.listdir(student_cache)
    for index, file_name in enumerate(file_list):
        file_path = os.path.abspath("{}/{}".format(student_cache, file_name))
        pipe_input.send((file_path, file_name, 'Teacher_' + cluster_name))
        util.process_bar(index + 1, len(file_list), 'Send task: {}/{}'.format(index + 1, len(file_list)))

    # 学生课表簇导入
    student_cache = os.path.abspath("{}/{}".format(data_path, "student_html"))
    file_list = os.listdir(student_cache)
    for index, file_name in enumerate(file_list):
        file_path = os.path.abspath("{}/{}".format(student_cache, file_name))
        pipe_input.send((file_path, file_name, 'Student_' + cluster_name))
        util.process_bar(index + 1, len(file_list), 'Send task: {}/{}'.format(index + 1, len(file_list)))

    [pipe_input.send(None) for i in range(run_config.CPU_CORE)]
    [process_list[i].join() for i in range(run_config.CPU_CORE)]


if __name__ == '__main__':
    # 读取配置文件
    run_env = 'development'
    if 'SERVICE_ENV' in os.environ and os.environ['SERVICE_ENV'] in Config.configs:
        run_env = os.environ['SERVICE_ENV']
    run_config = Config.configs[run_env]

    # 输入路径与簇名
    cache_path = os.path.abspath(input("Cache path："))
    cluster_list = ['2016-2017-1', '2016-2017-2', '2017-2018-1', '2017-2018-2']
    for cluster in cluster_list:
        cluster_path = os.path.abspath("{}/{}".format(cache_path, cluster))
        write_cluster(cluster, cluster_path)
        util.print_done("Add {} data finish !".format(cluster))
        time.sleep(1)
