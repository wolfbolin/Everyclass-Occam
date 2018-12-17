# -*- coding: UTF-8 -*-
# Common package
import re
from Crypto.Cipher import AES
from binascii import b2a_base64, a2b_base64
# Personal package
import util


def fill_16(text):
    """
    自动填充至十六位或十六的倍数
    :param text: 需要被填充的字符串
    :return: 已经被空白符填充的字符串
    """
    text += '\0' * (16 - (len(text) % 16))
    return str.encode(text)


def aes_encrypt(aes_key, aes_text):
    """
    使用密钥加密文本信息，将会自动填充空白字符
    :param aes_key: 加密密钥
    :param aes_text: 需要加密的文本
    :return: 经过加密的数据
    """
    # 初始化加密器
    cipher = AES.new(fill_16(aes_key), AES.MODE_ECB)
    # 先进行aes加密
    encrypt = cipher.encrypt(fill_16(aes_text))
    # 使用十六进制转成字符串形式
    encrypt_text = b2a_base64(encrypt).decode().replace('/', '-').strip()
    # 返回执行结果
    return encrypt_text


def aes_decrypt(aes_key, aes_text):
    """
    使用密钥解密文本信息，将会自动填充空白字符
    :param aes_key: 解密密钥
    :param aes_text: 需要解密的文本
    :return: 经过解密的数据
    """
    # 初始化解码器
    cipher = AES.new(fill_16(aes_key), AES.MODE_ECB)
    # 优先逆向解密十六进制为bytes
    decrypt = a2b_base64(aes_text.replace('-', '/').encode())
    # 使用aes解密密文
    decrypt_text = str(cipher.decrypt(decrypt), encoding='utf-8').replace('\0', '')
    # 返回执行结果
    return decrypt_text.strip()


def identifier_encrypt(cate, code):
    return aes_encrypt(util.get_config('aes_key'), "%s;%s" % (cate, code))


def identifier_decrypt(data):
    data = aes_decrypt(util.get_config('aes_key'), data)
    # 通过正则校验确定数据的正确性
    group = re.match('^(student|teacher|klass|room);([A-Za-z0-9]+)$', data)
    if group is None:
        raise ValueError('解密后的数据无法被合理解读，解密后数据:%s' % data)
    else:
        return group.group(1), group.group(2)


def check_semester(semester, mongo_pool):
    """
    检查输入的学期信息是否合理
    :param semester: 输入的学期信息
    :param mongo_pool: MongoDB连接池
    :return: 判定结果
    """
    semester_list = util.get_semester_list(mongo_pool)
    if semester in semester_list:
        return True
    else:
        return False
    # result = re.match('^([0-9]{4})-([0-9]{4})-([1-2])$', semester)
    # if result:
    #     part1 = int(result.group(1))
    #     part2 = int(result.group(2))
    #     if part1 < 2016 or part2 != part1 + 1:
    #         return False
    #     return True
    # else:
    #     return False


def make_week(time_list):
    """
    将周次信息合并为方便理解的中文字符串
    :param time_list: 周次列表
    :return: 简化的周次信息
    """
    # 自带去重排序效果（仅增强健壮性，不可依赖）
    time_list = list(set(time_list))
    # 判断异常
    if len(time_list) == 0:
        raise util.ErrorSignal('发现了没有周次的课程')
    # 判断一周的课程
    if len(time_list) == 1:
        return '%d/全周' % time_list[0]
    # 判断单双全周
    dt = []
    for i in range(1, len(time_list)):
        dt.append(time_list[i] - time_list[i - 1])
    dt = list(set(dt))
    if len(dt) == 1:  # 说明周次是有规律的
        if dt[0] == 1:  # 说明是全周课程
            return '%d-%d/全周' % (time_list[0], time_list[-1])
        if dt[0] == 2 and time_list[0] % 2 == 1:  # 说明是单周
            return '%d-%d/单周' % (time_list[0], time_list[-1])
        if dt[0] == 2 and time_list[0] % 2 == 0:  # 说明是双周
            return '%d-%d/双周' % (time_list[0], time_list[-1])
    # 不能进行单双全周聚合的时间
    time_list.append(999)  # 添加不可能存在的周次推动最后一组数据进入结果
    begin = time_list[0]
    result = ''
    for i in range(1, len(time_list)):
        if time_list[i] != time_list[i - 1] + 1:  # 说明时间发生了不连续的情况
            if time_list[i - 1] == begin:
                result += ',%d' % time_list[i - 1]
            else:
                result += ',%d-%d' % (begin, time_list[i - 1])
            begin = time_list[i]
    return result[1:] + '/全周'


def set_semester_list(mysql_conn, mongo_pool):
    # 查询现有的可用学期
    semester_list = []
    with mysql_conn.cursor() as cursor:
        sql = "show tables LIKE 'card_%';"
        cursor.execute(sql)
        result = cursor.fetchall()
        for card in result:
            group = re.match('card_([0-9]{4}-[0-9]{4}-[1-2])', card[0])
            if group:
                semester_list.append(group.group(1))

    # 向数据库中写入可用学期
    mongo_db = mongo_pool['common']
    mongo_db.update_one(
        filter={'semester_list': {'$exists': 1}},
        update={
            '$set': {
                'semester_list': semester_list
            }
        },
        upsert=True
    )


def get_semester_list(mongo_pool):
    # 从MongoDB中查询可用学期列表
    mongo_db = mongo_pool['common']
    result = mongo_db.find_one(
        filter={'semester_list': {'$exists': 1}},
        projection={'_id': 0})
    return result['semester_list']
