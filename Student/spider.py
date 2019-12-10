# coding=utf-8
import os
import Util
import time
import json
import random
from bs4 import BeautifulSoup


def pull_student_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    student_html_list = Util.read_html_list_data(conn, "student", version)
    Util.print_white("读取【学生列表】原始数据 [%d] 页" % len(student_html_list))

    # 获取鉴权cookie
    cookies = Util.Cookies()
    cookies.auth_cookies(config)

    # 获取总页数
    url = config["url"]["xspk"]
    cookies.set_url(url)
    http_data = {
        "PageNum": 1,
        "pageSize": "500"
    }
    http_result, _cookie = Util.safe_http_request("POST", url, headers=cookies.get_headers(),
                                                  cookies=cookies.get_cookies(),
                                                  data=http_data, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【学生列表】页码时，网络请求失败")

    # 解析网页数据
    try:
        soup = BeautifulSoup(http_result, "lxml")
        all_page_num = soup.find(id="totalPages").attrs["value"]
        all_page_num = int(all_page_num)
        mev_student_num = all_page_num * int(http_data["pageSize"])
    except AttributeError:
        Util.write_log("student_html_list", http_result)
        raise Util.ParseError("【学生列表】页码解析失败，解析页面已写入日志")
    Util.print_white("【学生列表】共计 [%d] 页, 大约 [%d] 条" % (all_page_num, mev_student_num))

    # 计算缺失的页面
    exist_page_num = []
    for page in student_html_list:
        exist_page_num.append(page["page"])
    task_page_num = list(set(range(1, all_page_num + 1)) - set(exist_page_num))
    Util.print_white("【学生列表】缺失 [%d] 页" % len(task_page_num))

    Util.print_blue("获取【学生列表】原始数据 [%s] 页" % len(task_page_num))
    comm_data = {
        "url": url,
        "method": "POST",
        "http_data": http_data,
        "proxies": config["proxy"],
        "version": str(version)
    }
    task_page_data = list({"page_num": page} for page in task_page_num)
    result_list = Util.turbo_multiprocess(config, student_list_concurrent, comm_data, task_page_data, add_cookies=True,
                                          max_core=2, max_thread=4, mysql_config=config["mysql-occam"])
    Util.print_azure("插入【学生列表】原始数据 [%s] 条 (RC: %d)" % (len(task_page_data), sum(result_list)))
    #################################
    # for page_num in task_page_num:
    #     http_data["PageNum"] = page_num
    #     http_result, _cookie = Util.safe_http_request("POST", url, headers=cookies.get_headers(),
    #                                                   cookies=cookies.get_cookies(),
    #                                                   data=http_data, proxies=config["proxy"])
    #     if http_result is None:
    #         Util.print_red("获取【教室列表】第 [%d] 页失败" % page_num)
    #         continue
    #     Util.print_white("获取【教室列表】第 [%d] 页成功" % page_num)
    #
    #     Util.write_html_list_data(conn, "student", version, page_num, http_result)


def student_list_concurrent(mysql_pool, task_data, cookies):
    http_data = task_data["http_data"]
    http_data["PageNum"] = task_data["page_num"]
    http_result, _cookie = Util.safe_http_request(task_data["method"], task_data["url"], headers=task_data["headers"],
                                                  cookies=cookies, data=http_data, proxies=task_data["proxies"])
    if http_result is None:
        Util.print_red("Pull student list page [%d] error" % task_data["page_num"])
        return 0

    rowcount = Util.write_html_list_data(mysql_pool.connection(), "student", task_data["version"],
                                         task_data["page_num"], http_result)

    return rowcount


def parse_student_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    student_html_list = Util.read_html_list_data(conn, "student", version)
    Util.print_white("读取【学生列表】原始数据 [%d] 页" % len(student_html_list))

    tag_meaning = {
        "": "",
        "序号": "id",
        "学生学号": "code",
        "学生姓名": "name",
        "电子邮箱": "email",
        "班级名称": "class",
        "校区名称": "campus",
        "院系名称": "faculty",
    }
    tag_index = {
        "id": 0,
        "code": 0,
        "name": 0,
        "class": 0,
        "campus": 0,
        "faculty": 0,
    }

    if len(student_html_list) == 0:
        return False

    # 预分析标签列
    for html in student_html_list:
        try:
            soup = BeautifulSoup(html["data"], "lxml")
            tag_list = soup.find('thead').find_all('th')
            for index, tag in enumerate(tag_list):
                if tag.string is None:
                    continue
                tag_key = tag_meaning[tag.string]
                tag_index[tag_key] = index
            break
        except AttributeError:
            Util.write_log("student_list_html", html["data"])
            Util.delete_html_list_data(conn, "student", version, html["page"])
            Util.print_red("【学生列表】解析表头失败，解析页面已写入日志，原数据已删除")
    Util.print_white("【学生列表】表头预分析完成：%s" % json.dumps(tag_index))

    # 解析页面数据
    crash_count = 0
    for num, html in enumerate(student_html_list):
        try:
            soup = BeautifulSoup(html["data"], "lxml")
            table_list = soup.find('tbody').find_all('tr')

            page_data = []
            for table_line in table_list:
                cell = table_line.find_all('td')

                student_line = {
                    "code": Util.purify_string(cell[tag_index["code"]].string.strip()),
                    "name": Util.purify_string(cell[tag_index["name"]].string.strip()),
                    "class": Util.purify_string(cell[tag_index["class"]].string.strip()),
                    "campus": Util.purify_string(cell[tag_index["campus"]].string.strip()),
                    "faculty": Util.purify_string(cell[tag_index["faculty"]].string.strip()),
                }
                page_data.append(student_line)

            Util.write_json_list_data(conn, "student", version, html["page"], json.dumps(page_data, ensure_ascii=False))
        except AttributeError:
            crash_count += 1
            Util.write_log("student_list_html", html["data"])
            Util.delete_html_list_data(conn, "student", version, html["page"])
            Util.print_red("【教室列表】第%d页解析失败，解析页面已写入日志，原数据已删除" % html["page"])
        Util.process_bar(num + 1, len(student_html_list), "【教室列表】写入进度")

    if crash_count == 0:
        Util.print_green("所有【教室列表】均正常解析并写入数据库")
    else:
        Util.print_yellow("部分【教室列表】写入失败，失败率：%d/%d" % (crash_count, len(student_html_list)))


if __name__ == '__main__':
    _config = Util.get_config("../config")
    pull_student_list(_config, "2019-11-27")
    parse_student_list(_config, "2019-11-27")
