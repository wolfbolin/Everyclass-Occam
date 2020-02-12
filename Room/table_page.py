# coding=utf-8
import json
import Util
import Config
import Common


def pull_room_list(config, version, semester):
    url = config["url"]["jslb"]
    params = {
        "method": "queryjs",
        "xnxq01id": str(semester)
    }
    http_result = Util.http_request("POST", url, params=params, proxies=config["proxy"])
    if http_result is None:
        raise Util.NetworkError("获取【活跃教室】时，网络请求失败")

    act_room_list = Util.js2json(http_result)
    print(act_room_list)

    conn = Util.mysql_conn(config, "mysql-occam")
    Common.write_json_data(conn, "act_room", version, 1, json.dumps(act_room_list, ensure_ascii=False))


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    pull_room_list(_config, "2019-11-27", "2019-2020-1")
