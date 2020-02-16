# coding=utf-8
import os
import re
import json
import Util
import pymysql
import requests
from requests.adapters import HTTPAdapter

useragent_path = os.path.dirname(__file__) + '/fake_useragent.json'


def purify_string(input_str):
    return input_str.replace('\xa0', '').replace('\u3000', '').strip()


def dict_link(dict1, dict2):
    res = dict1.copy()
    for key1 in dict1.keys():
        for key2 in dict2.keys():
            res[key1] = res[key1].replace("<{}>".format(key2), dict2[key2])
    return res


def js2json(js_str):
    data = str(js_str)
    data = data.replace("'", '"')
    data = data.replace("\\", "\\\\")
    data = data.replace("]qz--1", "]")
    data = re.sub(r'([,|{])([a-z]+)(:)', lambda x: '"'.join(x.groups()), data)
    data = json.loads(data)
    return data


def write_log(name="", data=""):
    log_path = os.path.abspath(Util.code_dir() + "/../log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    name = name + str(Util.unix_time()) + ".log"
    log_path = os.path.join(log_path, name)
    Util.print_white("写入日志：%s" % log_path)

    log_file = open(log_path, "w", encoding="utf-8")
    log_file.write(data)

    return name


def http_request(method, url, keep_cookie=False, **kwargs):
    client = requests.session()
    client.keep_alive = False
    client.mount("http://", HTTPAdapter(max_retries=5))
    client.mount("https://", HTTPAdapter(max_retries=5))

    http_result = None
    try:
        http_result = client.request(method=method, url=url, timeout=(2, 30), **kwargs)
    except requests.exceptions.ProxyError:
        Util.print_yellow("requests.exceptions.ProxyError:[%s]" % url)
    except requests.exceptions.ReadTimeout:
        Util.print_yellow("requests.exceptions.ReadTimeout:[%s]" % url)
    except requests.exceptions.ConnectionError:
        Util.print_yellow("requests.exceptions.ConnectionError:[%s]" % url)

    if http_result and keep_cookie:
        return http_result.text, http_result.cookies.get_dict()
    elif http_result:
        return http_result.text
    else:
        return None


def mysql_conn(config, db_key):
    config[db_key]['port'] = int(config[db_key]['port'])
    conn = pymysql.connect(**config[db_key])
    return conn


if __name__ == "__main__":
    write_log()
