# -*- coding: UTF-8 -*-
# Common package
# Personal package
import util


def search_semester_delete(conn, collection, semester):
    """
    清除MongoDB的指定集合中指定的学期信息
    :param conn: 数据库连接句柄
    :param collection: 需要清除的集合名称
    :param semester: 需要清除的学期
    :return: 受影响的数据条数
    """
    mongo_db = conn[collection]
    result = mongo_db.update_many(
        filter={},
        update={
            '$pull': {
                "semester": semester
            }
        }
    )
    return result.modified_count


def change_log_delete(conn, semester):
    """
    清除部分旧的修正日志
    :param conn: 数据库连接句柄
    :param semester: 需要清除的学期
    :return: 受影响的数据条数
    """
    mongo_db = conn['change_log']
    result = mongo_db.delete_many(
        filter={"semester": semester}
    )
    return result.deleted_count


def error_class_update(conn, semester, error_klass_list):
    """
    更新数据库中错误的课程数据
    :return: 受影响的记录数
    """
    rowcount = 0
    with conn.cursor() as cursor:
        for count, error_klass in enumerate(error_klass_list):
            remove_list = list(repr(x) for x in error_klass['remove'])
            conn.begin()
            sql = "DELETE FROM `student_link_%s` WHERE `cid` in ('%s');" % (semester, "','".join(remove_list))
            cursor.execute(sql)
            rowcount += cursor.rowcount
            sql = "DELETE FROM `teacher_link_%s` WHERE `cid` in ('%s');" % (semester, "','".join(remove_list))
            cursor.execute(sql)
            rowcount += cursor.rowcount
            sql = "DELETE FROM `card_%s` WHERE `cid` in ('%s');" % (semester, "','".join(remove_list))
            cursor.execute(sql)
            rowcount += cursor.rowcount
            conn.commit()
            util.process_bar(count + 1, len(error_klass_list), '已修正%d条错误教室数据' % (count + 1))
        return rowcount
