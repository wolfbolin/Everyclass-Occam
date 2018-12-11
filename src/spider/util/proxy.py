# -*- coding: utf-8 -*-
# Common package
import requests
# Personal package


def get_proxy():
    proxy_ip = requests.get("http://123.207.35.36:5010/get/").text
    return {"http": "http://{}".format(proxy_ip)}
