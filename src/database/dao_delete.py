# -*- coding: UTF-8 -*-
# Common package
# Personal package
import util


def semester_delete(conn, collection, semester):
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
