# coding=utf-8


# 写入教室信息
def write_room_info(conn, room_data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `course` (`code`, `name`, `type`, `faculty`) " \
          "VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, args=[room_data["code"], room_data["name"], room_data["type"],
                              room_data["faculty"]])
    conn.commit()
