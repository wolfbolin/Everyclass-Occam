# coding=utf-8
import time
import json
import Util
import Config
import Common
from math import ceil
from bs4 import BeautifulSoup


def fetch_list_data(config, version, task_name, task_word, tag_dict, url_index, page_size):
    """
    批量更新列表信息数据
    :param config:  配置文件
    :param version:  当前版本
    :param task_name:  任务名称 eg: 学生列表
    :param task_word:  关键字 eg: student
    :param tag_dict:  表头映射关系
    :param url_index:  链接关键字
    :param page_size:  分页大小
    :return:
    """
    # 预处理参数
    task_key = (task_name, task_word)
    headers, cookies = Common.auth_cookie(config)
    tag_index = dict(zip(tag_dict.values(), [0] * len(tag_dict)))

    # 预获取页面信息
    http_result = pull_list_page(config, version, task_key, url_index, headers, 1, page_size)

    # 预分析页面信息
    all_page_num, tag_index = parse_page_info(config, task_key, http_result, tag_dict, tag_index, page_size)

    # 获取已下载信息
    _, exist_page_num = Common.read_exist_json_data(config, version, task_key)
    task_page_num = list(set(range(1, all_page_num + 1)) - set(map(int, exist_page_num)))
    if len(task_page_num) == 0:
        Util.print_azure("该版本【%s】无需下载更新" % task_name)
        return False

    # 下载完整数据
    for page_num in task_page_num:
        Util.print_white("【%s】正在下载第%s页..." % (task_name, page_num), end='')

        # 尝试获取页面
        time_start = time.time()
        http_result = pull_list_page(config, version, task_key, url_index, headers, page_num, page_size)

        # 解析页面信息
        parse_list_page(config, version, task_key, tag_index, http_result, page_num)
        time_end = time.time()

        Util.print_green("OK", tag='', end='')
        Util.print_yellow("(%ss)" % ceil(time_end - time_start), tag='')

    return True


# 预分析页面信息
def parse_page_info(config, task_key, http_result, tag_dict, tag_index, page_size):
    soup = BeautifulSoup(http_result, "lxml")

    # 解析页码数据
    try:
        all_page_num = soup.find(id="totalPages").attrs["value"]
        all_page_num = int(all_page_num)
        mev_line_num = all_page_num * int(page_size)
    except AttributeError:
        Util.write_log("list_page_info", http_result)
        raise Util.ParseError("【%s】页码解析失败，解析页面已写入日志" % task_key[0])
    Util.print_white("【%s】页码数据：共计 [%d] 页, 大约 [%d] 条" % (task_key[0], all_page_num, mev_line_num))

    # 解析映射关系
    try:
        tag_list = soup.find('thead').find_all('th')
        for index, tag in enumerate(tag_list):
            if tag.string is None:
                continue
            tag_key = tag_dict[tag.string]
            tag_index[tag_key] = index
    except AttributeError:
        Util.write_log("list_page_info", http_result)
        raise Util.ParseError("【%s】映射解析失败，解析页面已写入日志" % task_key[0])
    Util.print_white("【{}】映射关系：{}".format(task_key[0], tag_index))

    return all_page_num, tag_index


# 获取列表页面
def pull_list_page(config, version, task_key, url_index, headers, page_num, page_size):
    conn = Util.mysql_conn(config, "mysql-occam")

    url = config["url"][url_index]
    http_data = {
        "PageNum": int(page_num),
        "pageSize": str(page_size)
    }
    http_result = Util.http_request("POST", url, headers=headers, data=http_data, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【%s】第%s页时，网络请求失败" % (task_key[0], page_num))

    # 写入已获取的数据
    Common.write_html_data(conn, task_key[1], version, page_num, http_result)

    return http_result


def parse_list_page(config, version, task_key, tag_index, http_result, page_num):
    conn = Util.mysql_conn(config, "mysql-occam")

    # 解析页面数据
    try:
        soup = BeautifulSoup(http_result, "lxml")
        table_list = soup.find('tbody').find_all('tr')

        page_data = []
        for table_line in table_list:
            cell = table_line.find_all('td')
            data_line = dict()
            for key in tag_index:
                data_line[key] = Util.purify_string(cell[tag_index[key]].string.strip())
            page_data.append(data_line)

        Common.write_json_data(conn, task_key[1], version, page_num, json.dumps(page_data, ensure_ascii=False))
    except AttributeError:
        Util.write_log("pull_%s_data" % task_key[1], http_result)
        Common.delete_html_data(conn, task_key[1], version, page_num)
        Util.print_red("【%s】第%d页解析失败，解析页面已写入日志，原数据已删除" % (task_key[0], page_num))


def merge_page_info(config, version, task_name, task_word, dao_func):
    task_key = (task_name, task_word)
    occam_conn = Util.mysql_conn(config, "mysql-occam")
    entity_conn = Util.mysql_conn(config, "mysql-entity")

    # 读取页面信息
    page_data_list = Common.read_json_data(occam_conn, task_key[1], version)

    data_bin = list()
    for page_data in page_data_list:
        data_bin.extend(json.loads(page_data["data"]))

    for index, line_data in enumerate(data_bin):
        dao_func(entity_conn, version, line_data)
        Util.process_bar(index + 1, len(data_bin), "写入【%s】" % task_key[0])


if __name__ == "__main__":
    tag_meaning = {
        "序号": "id",
        "学生学号": "code",
        "学生姓名": "name",
        "电子邮箱": "email",
        "班级名称": "class",
        "校区名称": "campus",
        "院系名称": "faculty",
    }

    _config = Config.load_config("../Config")
    fetch_list_data(_config, "2019-11-27", "学生列表", "student", tag_meaning, "xspk", 200)
