# coding=utf-8
import os
import Util
import pymysql
import requests
from requests.adapters import HTTPAdapter

useragent_path = os.path.dirname(__file__) + '/fake_useragent.json'


def purify_string(str):
    return str.replace('\xa0', '').replace('\u3000', '').strip()


def write_log(name="", data=""):
    log_path = os.path.abspath(Util.code_dir() + "/../log")
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    name = name + str(Util.unix_time())
    log_path = os.path.join(log_path, "%s.log" % name)
    Util.print_white("写入日志：%s" % log_path)

    log_file = open(log_path, "w", encoding="utf-8")
    log_file.write(data)


def safe_http_request(method, url, **kwargs):
    client = requests.session()
    client.keep_alive = False
    client.mount("http://", HTTPAdapter(max_retries=5))
    client.mount("https://", HTTPAdapter(max_retries=5))

    http_result = None
    try:
        http_result = client.request(method=method, url=url, timeout=5, **kwargs)
    except requests.exceptions.ProxyError:
        Util.print_yellow("requests.exceptions.ProxyError:[%s]" % url)
    except requests.exceptions.ReadTimeout:
        Util.print_yellow("requests.exceptions.ReadTimeout:[%s]" % url)
    except requests.exceptions.ConnectionError:
        Util.print_yellow("requests.exceptions.ConnectionError:[%s]" % url)

    if http_result:
        return http_result.text, http_result.cookies.get_dict()
    else:
        return None, None


def mysql_conn(config, db_key):
    config[db_key]['port'] = int(config[db_key]['port'])
    conn = pymysql.connect(**config[db_key])
    return conn


if __name__ == "__main__":
    write_log()
