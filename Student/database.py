# coding=utf-8


# 写入教室信息
def write_student_info(conn, room_data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `student` (`code`, `name`,`email`, `class`, `campus`, `faculty`) " \
          "VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[room_data["code"], room_data["name"], room_data["email"], room_data["class"],
                              room_data["campus"], room_data["faculty"]])
    conn.commit()
