# coding=utf-8


# 写入教室信息
def write_room_info(conn, version, room_data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `room` (`code`, `name`, `campus`, `building`, `version`) " \
          "VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[room_data["code"], room_data["name"], room_data["campus"],
                              room_data["building"], version])
    conn.commit()

