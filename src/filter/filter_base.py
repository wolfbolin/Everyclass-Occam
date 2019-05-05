# -*- coding: utf-8 -*-
# Common package
import re
# Personal package
import util


def room_all(data_set):
    """
    单线程处理函数
    完成对所有教室数据的校验
    :param data_set: 所有教室的数据
    :return: 经过过滤的数据
    """
    result = []
    for room in data_set:
        if 'code' not in room or 'name' not in room \
                or 'building' not in room or 'campus' not in room:
            raise util.ErrorSignal('课程{}缺少字段'.format(room))
        room['code'] = room['code'].replace('\xa0', '').replace('\u3000', '').strip()
        room['name'] = room['name'].replace('\xa0', '').replace('\u3000', '').strip()
        room['campus'] = room['campus'].replace('\xa0', '').replace('\u3000', '').strip()
        room['building'] = room['building'].replace('\xa0', '').replace('\u3000', '').strip()
        room['name'] = util.sbc2dbc(room['name'])
        room['building'] = util.sbc2dbc(room['building'])
        if room not in result:
            result.append(room)
    return result


def check_semester(semester):
    """
    检查输入的学期信息是否合理
    :param semester: 输入的学期信息
    :return: 判定结果
    """
    result = re.match('^([0-9]{4})-([0-9]{4})-([1-2])$', semester)
    if result:
        part1 = int(result.group(1))
        part2 = int(result.group(2))
        if part1 < 2016 or part2 != part1 + 1:
            return False
        return True
    else:
        return False


def regex_converter(data_set):
    """
    根据正则处理生成搜索数据
    :param data_set: 数据集
    :return: 完成匹配的数据
    """
    for item in data_set:
        result = re.match(item['regex'], item['name'])
        key = []
        if result:
            for pattern in item['pattern']:
                key_slice = []
                for mark in pattern:
                    if type(mark) == 'str':
                        key_slice.append(mark)
                    else:
                        key_slice.append(result.group(int(mark)))
                key.append(''.join(key_slice))
        else:
            raise BaseException('正则：{}，文本：{}。无法匹配！！！'.format(item['regex'], item['name']))
        item['key'] = key
    return data_set
