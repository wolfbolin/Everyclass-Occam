# -*- coding: utf-8 -*-
# Common package
import json
# Personal package
import util


def error_room(semester, error_room_list, room_list):
    """
    纠正教室异常数据
    :param semester: 数据学期
    :param error_room_list: 异常数据列表
    :param room_list: 教室列表源数据
    :return: 修正数据
    :return: 修改记录
    """
    room_index = {}
    for room in room_list:
        room_index[room['name']] = room
    change_log = []
    for room in error_room_list:
        if room['room'] in room_index:
            new_room = room_index[room['room']]
            # 写入修改日志
            change_log.append({
                'semester': semester,
                'type': '无效的教室信息映射',
                'message': '教室%s将修改%s为%s' % (room['room'], room['room_code'], new_room['code'])
            })
            util.print_w(change_log[-1]['message'])
            # 修改数据
            room['room_code'] = new_room['code']
        else:
            # 写入修改日志
            change_log.append({
                'semester': semester,
                'type': '无效的教室信息映射',
                'message': '教室%s无法在数据库中找到，已置为空教室' % room['room']
            })
            util.print_w(change_log[-1]['message'])
            # 修改数据
            room['room_code'] = ''
    return error_room_list, change_log


def error_card(semester, doubt_list):
    """
    纠正课程异常数据
    :param semester: 数据学期
    :param doubt_list: 可疑数据
    :return: 数据纠正方案
    """
    error_list = []
    change_log = []
    for item in doubt_list:
        reserved_key = []
        remove_key = []
        keys = list(item['map'].keys())  # 获取该疑点的所有cid值
        for index1, key1 in enumerate(keys):
            if key1 in remove_key:
                # 若该键已确认删除，跳过
                continue
            else:
                # 添加保留的cid
                reserved_key.append(key1)

            for index2, key2 in enumerate(keys[index1 + 1:]):
                if key2 in remove_key:
                    # 若该键已确认删除，跳过
                    continue
                # 计算集合差值
                dt_list = list(set(item['map'][key1]) - set(item['map'][key2]))
                # 判断是否完全相同
                if len(dt_list) == 0 and len(item['map'][key1]) - len(dt_list) == len(item['map'][key2]):
                    # 写入修改日志
                    change_log.append({
                        'semester': semester,
                        'type': '课程信息重复',
                        'message': 'cid: %s 与cid: %s 合并，cid: %s 被删除' % (key1, key2, key2)
                    })
                    util.print_w(change_log[-1]['message'])
                    # 添加被删除的cid
                    remove_key.append(key2)
        if len(remove_key) != 0:
            error_list.append(item)
            error_list[-1]['reserved'] = reserved_key
            error_list[-1]['remove'] = remove_key
    return error_list, change_log
