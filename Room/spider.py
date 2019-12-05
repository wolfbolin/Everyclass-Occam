# coding=utf-8
import os
import Util
from Room.database import *
from bs4 import BeautifulSoup


def pull_room_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    room_list_html = read_room_list(conn, version)

    # 获取鉴权cookie
    auth_cookies = Util.auth_cookie(config)

    # 获取总页数
    url = config["url"]["jspk"]
    headers = Util.access_header(url)
    http_data = {
        "PageNum": 1,
        "pageSize": "50"
    }
    http_result, cookies = Util.safe_http_request("POST", url, headers=headers, cookies=auth_cookies,
                                                  data=http_data, proxies=config["proxy"])

    if http_result is None:
        raise Util.NetworkError("Get room page num failed.")

    # 解析网页数据
    try:
        soup = BeautifulSoup(http_result, "lxml")
        all_page_num = soup.find(id="totalPages").attrs["value"]
        all_page_num = int(all_page_num)
    except AttributeError:
        Util.write_log("room_list_html", http_result)
        raise Util.ParseError("【教室列表】页码解析失败")

    Util.print_white("【教室列表】共计 [%d] 页" % all_page_num)

    # 计算缺失的页面
    exist_page_num = []
    for page in room_list_html:
        exist_page_num.append(page["page"])

    task_page_num = list(set(range(1, all_page_num + 1)) - set(exist_page_num))

    Util.print_white("【教室列表】缺失 [%d] 页" % len(task_page_num))

    for page_num in task_page_num:
        http_data["PageNum"] = page_num
        http_result, cookies = Util.safe_http_request("POST", url, headers=headers, cookies=auth_cookies,
                                                      data=http_data, proxies=config["proxy"])
        if http_result is None:
            Util.print_red("获取【教室列表】第 [%d] 页失败" % page_num)

        Util.print_white("获取【教室列表】第 [%d] 页成功" % page_num)

        write_room_list(conn, version, page_num, http_result)


if __name__ == '__main__':
    _config = Util.get_config("../config")
    pull_room_list(_config, Util.str_time("%Y-%m-%d"))
