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
    semester = "2019-2020-2"
    conn = Util.mysql_conn(config, "mysql-entity")
    Common.delete_semester_data(conn, "lesson", semester)
    Room.update(config, semester, config["semester"][semester])
    Course.update(config, semester, config["semester"][semester])
    Student.update(config, semester, config["semester"][semester])
    Teacher.update(config, semester, config["semester"][semester])
    Preprocess.lesson_data(config, semester)

    # 重新计算所有学期数据
    # for semester in config["semester"]:
    #     # 重新计算对象信息
    #     Room.update(config, semester, config["semester"][semester])
    #     Course.update(config, semester, config["semester"][semester])
    #     Student.update(config, semester, config["semester"][semester])
    #     Teacher.update(config, semester, config["semester"][semester])
    #
    #     # 重新完成数据预处理
    #     Preprocess.lesson_data(config, semester)

    Preprocess.search_data(config)
