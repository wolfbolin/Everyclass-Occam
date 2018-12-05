# -*- coding: UTF-8 -*-
# Common package
import re
import base64
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


# Personal package

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
    encrypt_text = b2a_hex(encrypt).decode()
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
    decrypt = a2b_hex(aes_text.encode())
    # 使用aes解密密文
    decrypt_text = str(cipher.decrypt(decrypt), encoding='utf-8').replace('\0', '')
    # 返回执行结果
    return decrypt_text.strip()


def identifier_encrypt(key, cate, code):
    return aes_encrypt(key, "%s;%s" % (cate, code))


def identifier_decrypt(key, data):
    data = aes_decrypt(key, data)
    # 通过正则校验确定数据的正确性
    group = re.match('^(student|teacher|klass|room);([A-Za-z0-9]+)$', data)
    if group is None:
        raise ValueError('解密后的数据无法被合理解读，解密后数据:%s' % data)
    else:
        return group.group(1), group.group(2)


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
