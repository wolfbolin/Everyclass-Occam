# coding=utf-8


# 写入教室信息
def write_room_info(conn, version, room_data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `room` (`code`, `name`, `type`, `seat`, `effect_seat`," \
          "`exam_seat`, `campus`, `building`, `version`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[room_data["code"], room_data["name"], room_data["type"], room_data["seat"],
                              room_data["effect_seat"], room_data["exam_seat"], room_data["campus"],
                              room_data["building"], version])
    conn.commit()
