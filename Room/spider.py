# coding=utf-8
import os
import Util
import json
from Room.database import *
from bs4 import BeautifulSoup


def pull_room_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    room_list_html = Util.read_html_list_data(conn, "room", version)
    Util.print_white("读取【教室列表】原始数据 [%d] 页" % len(room_list_html))

    # 获取鉴权cookie
    cookies = Util.Cookies()
    cookies.auth_cookies(config)

    # 获取总页数
    url = config["url"]["jspk"]
    cookies.set_url(url)
    http_data = {
        "PageNum": 1,
        "pageSize": "30"
    }
    http_result, _cookie = Util.safe_http_request("POST", url, headers=cookies.get_headers(),
                                                  cookies=cookies.get_cookies(),
                                                  data=http_data, proxies=config["proxy"])

    if http_result is None:
        raise Util.NetworkError("获取【教室列表】页码时，网络请求失败")

    # 解析网页数据
    try:
        soup = BeautifulSoup(http_result, "lxml")
        all_page_num = soup.find(id="totalPages").attrs["value"]
        all_page_num = int(all_page_num)
        mev_student_num = all_page_num * int(http_data["pageSize"])
    except AttributeError:
        Util.write_log("room_list_html", http_result)
        raise Util.ParseError("【教室列表】页码解析失败，解析页面已写入日志")
    Util.print_white("【教室列表】共计 [%d] 页, 大约 [%d] 条" % (all_page_num, mev_student_num))

    # 计算缺失的页面
    exist_page_num = []
    for page in room_list_html:
        exist_page_num.append(page["page"])
    task_page_num = list(set(range(1, all_page_num + 1)) - set(exist_page_num))
    Util.print_white("【教室列表】缺失 [%d] 页" % len(task_page_num))

    for page_num in task_page_num:
        http_data["PageNum"] = page_num
        http_result, _cookie = Util.safe_http_request("POST", url, headers=cookies.get_headers(),
                                                      cookies=cookies.get_cookies(),
                                                      data=http_data, proxies=config["proxy"])
        if http_result is None:
            Util.print_red("获取【教室列表】第 [%d] 页失败" % page_num)
            continue
        Util.print_white("获取【教室列表】第 [%d] 页成功" % page_num)
        Util.write_html_list_data(conn, "room", version, page_num, http_result)


def parse_room_list(config, version):
    # 读取已下载页面
    conn = Util.mysql_conn(config, "mysql-occam")
    room_html_list = Util.read_html_list_data(conn, "room", version)

    tag_meaning = {
        "": "",
        "序号": "id",
        "教室编号": "code",
        "教室名称": "name",
        "所在校区": "campus",
        "所在教学楼": "building",
    }
    tag_index = {
        "id": 0,
        "code": 0,
        "name": 0,
        "campus": 0,
        "building": 0
    }

    if len(room_html_list) == 0:
        return False

    # 预分析标签列
    for html in room_html_list:
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
            Util.write_log("room_html_list", html["data"])
            Util.delete_html_list_data(conn, "room", version, html["page"])
            Util.print_red("【教室列表】解析标签列失败，解析页面已写入日志，原数据已删除")
    Util.print_white("【教室列表】表头预分析完成：%s" % json.dumps(tag_index))

    # 解析页面数据
    crash_count = 0
    for html in room_html_list:
        try:
            soup = BeautifulSoup(html["data"], "lxml")
            table_list = soup.find('tbody').find_all('tr')

            page_data = []
            for table_line in table_list:
                cell = table_line.find_all('td')

                room_line = {
                    "code": Util.purify_string(cell[tag_index["code"]].string.strip()),
                    "name": Util.purify_string(cell[tag_index["name"]].string.strip()),
                    "campus": Util.purify_string(cell[tag_index["campus"]].string.strip()),
                    "building": Util.purify_string(cell[tag_index["building"]].string.strip()),
                }
                page_data.append(room_line)

            Util.write_json_list_data(conn, "room", version, html["page"], json.dumps(page_data, ensure_ascii=False))
        except AttributeError:
            crash_count += 1
            Util.write_log("room_html_list", html["data"])
            Util.delete_html_list_data(conn, "room", version, html["page"])
            Util.print_red("【教室列表】第%d页解析失败，解析页面已写入日志，原数据已删除" % html["page"])

    if crash_count == 0:
        Util.print_green("所有【教室列表】均正常解析并写入数据库")
    else:
        Util.print_yellow("部分【教室列表】写入失败，失败率：%d/%d" % (crash_count, len(room_html_list)))


if __name__ == '__main__':
    _config = Util.get_config("../config")
    pull_room_list(_config, "2019-11-27")
    parse_room_list(_config, "2019-11-27")
