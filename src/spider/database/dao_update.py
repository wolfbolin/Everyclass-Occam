# -*- coding: UTF-8 -*-
# Common package
# Personal package


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
            sql = "INSERT INTO  `all_room` (`campus`, `building`, `name`) VALUES ('%s', '%s', '%s') " \
                  "ON DUPLICATE KEY UPDATE rid = rid;" \
                  % (room['campus'], room['building'], room['name'])
            cursor.execute(sql)
            rowcount += cursor.rowcount
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
        sql = "INSERT INTO `all_teacher` (`code`,`name`,`unit`,`title`,`degree`) VALUES ('%s','%s','%s','%s','%s') " \
              "ON DUPLICATE KEY UPDATE `name`='%s', `unit`='%s', `title`='%s', `degree`='%s';" \
              % (teacher_data['code'],
                 teacher_data['name'], teacher_data['unit'], teacher_data['title'], teacher_data['degree'],
                 teacher_data['name'], teacher_data['unit'], teacher_data['title'], teacher_data['degree'])
        cursor.execute(sql)
        rowcount = cursor.rowcount
        return rowcount


def student_update(student_data):
    """
    完成学生的信息在学生总表上插入，若学生编号已存在则跳过
    学生信息的批量插入需要由控制器完成
    :param student_data: 数据字典，一名学生的信息+数据库链接句柄
    :return: 受影响的数据行数
    """
    conn = student_data['mysql_pool'].connection()
    with conn.cursor() as cursor:
        # 尝试插入该学生信息，若出现UNIQUE重复则自动更新数据
        sql = "INSERT INTO `all_student`(`code`,`name`,`klass`,`deputy`,`campus`)VALUES('%s','%s','%s','%s','%s') " \
              "ON DUPLICATE KEY UPDATE `name`='%s',`klass`='%s',`deputy`='%s',`campus`='%s';" \
              % (student_data['code'],
                 student_data['name'], student_data['klass'], student_data['deputy'], student_data['campus'],
                 student_data['name'], student_data['klass'], student_data['deputy'], student_data['campus'])
        cursor.execute(sql)
        rowcount = cursor.rowcount
        return rowcount
