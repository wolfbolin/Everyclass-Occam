# -*- coding: UTF-8 -*-
# Common package
import pypinyin
# Personal package
import util


def room_update(room_data, conn):
    """
    单线程处理函数
    将所有的教室信息写入数据库中
    :param room_data: 教室信息
    :param conn: 数据库连接
    :return: 受影响的数据行数
    """
    rowcount = 0
    with conn.cursor() as cursor:
        for count, room in enumerate(room_data):
            # 尝试插入该教室信息，若出现UNIQUE重复则自动忽略
            sql = "INSERT INTO  `room_all` (`code`, `name`, `campus`, `building`) VALUES ('%s', '%s', '%s', '%s') " \
                  "ON DUPLICATE KEY UPDATE `rid` = '%s';" \
                  % (room['code'], room['name'], room['campus'], room['building'], room['name'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
            util.process_bar(count + 1, len(room_data), '完成%s项，修改%s行' % (count + 1, rowcount))
        return rowcount


def teacher_update(teacher_data):
    """
    完成教师信息的更新，不存在的插入，存在的更新
    :param teacher_data: 数据字典，一名老师的信息+数据库链接句柄
    :return: 受影响的数据行数
    """
    conn = teacher_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 尝试插入该教师信息，若出现UNIQUE重复则自动更新数据
        sql = "INSERT INTO `teacher_all` (`code`,`name`,`unit`,`title`,`degree`) VALUES ('%s','%s','%s','%s','%s') " \
              "ON DUPLICATE KEY UPDATE `name`='%s', `unit`='%s', `title`='%s', `degree`='%s';" \
              % (teacher_data['code'],
                 teacher_data['name'], teacher_data['unit'], teacher_data['title'], teacher_data['degree'],
                 teacher_data['name'], teacher_data['unit'], teacher_data['title'], teacher_data['degree'])
        cursor.execute(sql)
        rowcount = cursor.rowcount
        return rowcount


def student_update(student_data):
    """
    多线程函数
    完成学生的信息在学生总表上插入，若学生编号已存在则跳过
    学生信息的批量插入需要由控制器完成
    :param student_data: 数据字典，一名学生的信息+数据库链接句柄
    :return: 受影响的数据行数
    """
    conn = student_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 尝试插入该学生信息，若出现UNIQUE重复则自动更新数据
        sql = "INSERT INTO `student_all`(`code`,`name`,`klass`,`deputy`,`campus`)VALUES('%s','%s','%s','%s','%s') " \
              "ON DUPLICATE KEY UPDATE `name`='%s',`klass`='%s',`deputy`='%s',`campus`='%s';" \
              % (student_data['code'],
                 student_data['name'], student_data['klass'], student_data['deputy'], student_data['campus'],
                 student_data['name'], student_data['klass'], student_data['deputy'], student_data['campus'])
        cursor.execute(sql)
        rowcount = cursor.rowcount
        return rowcount


def search_update(object_data):
    """
    多线程函数
    将某学期学生的信息写入文档库中
    :param object_data: 数据字典，一名学生的信息+数据库链接句柄+学期信息
    :return: 受影响的数据行数
    """
    rowcount = 0
    conn = object_data['mongo_pool']
    # 生成名字的拼音与缩写
    full_pinyin = pypinyin.pinyin(object_data['name'], errors='ignore', style=pypinyin.Style.NORMAL)
    full_pinyin = ''.join(list(x[0] for x in full_pinyin)).strip()
    first_pinyin = pypinyin.pinyin(object_data['name'], errors='ignore', style=pypinyin.Style.FIRST_LETTER)
    first_pinyin = ''.join(list(x[0] for x in first_pinyin)).strip()
    # 写入索引记录
    search_data = {k: object_data[k] for k in object_data['conversion']}
    # 写入学号索引
    rowcount += search_update_row(conn, object_data['code'], object_data['code'], object_data['name'],
                                  object_data['type'], object_data['semester'], search_data)
    # 写入姓名索引
    rowcount += search_update_row(conn, object_data['name'], object_data['code'], object_data['name'],
                                  object_data['type'], object_data['semester'], search_data)
    if len(full_pinyin) > 0:
        rowcount += search_update_row(conn, full_pinyin, object_data['code'], object_data['name'],
                                      object_data['type'], object_data['semester'], search_data)
    if len(first_pinyin) > 0:
        rowcount += search_update_row(conn, first_pinyin, object_data['code'], object_data['name'],
                                      object_data['type'], object_data['semester'], search_data)
    return rowcount


def search_update_row(conn, key, code, name, type, semester, data):
    """
    向数据库中更新单条搜索关联
    :param conn: MongoDB数据库连接
    :param key: 索引值
    :param code: 实体编号
    :param name: 实体名称
    :param type: 实体类型
    :param semester: 学期列表
    :param data: 附加数据表
    :return: 受影响的记录数
    """
    # 设定文档集
    mongo_db = conn['search']
    # 尝试更新学期在已知字段中
    # 此人记录不存在，创建该记录
    result = mongo_db.update_one(
        filter={
            "key": key,
            "code": code
        },
        update={
            "$setOnInsert": {
                "name": name,
                "type": type,
                "data": data,
            },
            "$addToSet": {
                "semester": semester
            }
        },
        upsert=True
    )
    if result.upserted_id:
        return 1
    else:
        return result.modified_count


def error_room_update(conn, semester, error_room_list):
    """
    更新数据库中错误的教室数据
    :return: 受影响的记录数
    """
    rowcount = 0
    with conn.cursor() as cursor:
        for count, error_room in enumerate(error_room_list):
            sql = "UPDATE `card_%s` SET `roomID`='%s' WHERE `cid`=%s;" \
                  % (semester, error_room['roomID'], error_room['cid'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
            util.process_bar(count + 1, len(error_room_list), '已修正%d条错误教室数据' % (count + 1))
        return rowcount


