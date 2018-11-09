# -*- coding: utf-8 -*-
# Common package
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
        if room not in result:
            result.append(room)
    return result
