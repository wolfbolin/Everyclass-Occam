# coding=utf-8


# 写入教师信息
def write_teacher_info(conn, room_data):
    cursor = conn.cursor()
    sql = "REPLACE INTO `teacher` (`code`, `name`, `title`, `degree`, `department`, `section`) " \
          "VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, args=[room_data["code"], room_data["name"], room_data["title"], room_data["degree"],
                              room_data["department"], room_data["section"]])
    conn.commit()
