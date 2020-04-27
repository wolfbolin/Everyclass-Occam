# coding=utf-8
import Util
import Room
import Common
import Config
import Course
import Student
import Teacher
import Preprocess

if __name__ == "__main__":
    config = Config.load_config("./Config")

    # 更新单一学期数据
    semester = input("semester: ")
    conn = Util.mysql_conn(config, "mysql-entity")
    Common.delete_semester_data(conn, "lesson", semester)
    Room.update(config, semester, config["schedule"][semester])
    Course.update(config, semester, config["schedule"][semester])
    Student.update(config, semester, config["schedule"][semester])
    Teacher.update(config, semester, config["schedule"][semester])
    Preprocess.lesson_data(config, semester)

    Preprocess.search_data(config)
