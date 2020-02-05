# coding=utf-8
import Util
import json
import Config
import Common
from bs4 import BeautifulSoup


def update_list_data(config, version):
    headers, cookies = Common.auth_cookie(_config)
    all_page_num, tag_index = list_page_info(_config)
    _, exist_page_num = read_html_data(config, version)
    task_page_num = list(set(range(1, all_page_num + 1)) - set(exist_page_num))

    if len(task_page_num) == 0:
        Util.print_white("该版本【教室列表】无需下载更新")

    for page_num in task_page_num:
        Util.print_white("正在下载【教师列表】第%s页..." % page_num, end='')
        pull_room_list(config, version, tag_index, headers, page_num)
        Util.print_green("OK", tag='')

    room_json_list, _ = read_html_data(config, version)

    data_pack = list()
    for page in room_json_list:
        data_pack.extend(json.loads(page["data"]))

    print(data_pack)


# 读取已完成的页面
def read_html_data(config, version):
    conn = Util.mysql_conn(config, "mysql-occam")
    room_json_list = Common.read_json_list_data(conn, "room", version)
    exist_page_num = set()
    for page in room_json_list:
        exist_page_num.add(int(page["page"]))
    Util.print_white("读取【教室列表】共%d页" % len(room_json_list))
    return room_json_list, exist_page_num


# 获取总页数和映射
def list_page_info(config):
    # 获取Cookies
    headers, cookies = Common.auth_cookie(config)

    # 尝试获取页面
    url = config["url"]["jspk"]
    http_data = {
        "PageNum": 1,
        "pageSize": "50"
    }
    http_result = Util.http_request("POST", url, headers=headers, data=http_data, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【教室列表】页码时，网络请求失败")

    # 解析网页数据
    soup = BeautifulSoup(http_result, "lxml")

    # 解析页码数据
    try:
        all_page_num = soup.find(id="totalPages").attrs["value"]
        all_page_num = int(all_page_num)
        mev_student_num = all_page_num * int(http_data["pageSize"])
    except AttributeError:
        Util.write_log("list_page_info", http_result)
        raise Util.ParseError("【教室列表】页码解析失败，解析页面已写入日志")
    Util.print_white("【教室列表】页码数据：共计 [%d] 页, 大约 [%d] 条" % (all_page_num, mev_student_num))

    # 解析映射关系
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
    try:
        tag_list = soup.find('thead').find_all('th')
        for index, tag in enumerate(tag_list):
            if tag.string is None:
                continue
            tag_key = tag_meaning[tag.string]
            tag_index[tag_key] = index
    except AttributeError:
        Util.write_log("list_page_info", http_result)
        raise Util.ParseError("【教室列表】映射解析失败，解析页面已写入日志")
    Util.print_white("【教室列表】映射关系：{}".format(tag_index))

    return all_page_num, tag_index


def pull_room_list(config, version, tag_index, headers, page_num):
    conn = Util.mysql_conn(config, "mysql-occam")

    # 尝试获取页面
    url = config["url"]["jspk"]
    http_data = {
        "PageNum": page_num,
        "pageSize": "50"
    }
    http_result = Util.http_request("POST", url, headers=headers, data=http_data, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【教室列表】第%s页时，网络请求失败" % page_num)

    # 写入已获取的数据
    Common.write_html_list_data(conn, "room", version, page_num, http_result)

    # 解析页面数据
    crash_count = 0
    try:
        soup = BeautifulSoup(http_result, "lxml")
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

        Common.write_json_list_data(conn, "room", version, page_num, json.dumps(page_data, ensure_ascii=False))
    except AttributeError:
        crash_count += 1
        Util.write_log("pull_room_data", http_result)
        Common.delete_html_list_data(conn, "room", version, page_num)
        Util.print_red("【教室列表】第%d页解析失败，解析页面已写入日志，原数据已删除" % page_num)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update_list_data(_config, "2019-11-27")
