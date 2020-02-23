# coding=utf-8
import Room
import Config
import Course
import Student
import Teacher
import Preprocess

if __name__ == "__main__":
    config = Config.load_config("./Config")

    # 重新计算所有学期数据
    for semester in config["semester"]:
        # 重新计算对象信息
        Room.update(config, semester, config["semester"][semester])
        Course.update(config, semester, config["semester"][semester])
        Student.update(config, semester, config["semester"][semester])
        Teacher.update(config, semester, config["semester"][semester])

        # 重新完成数据预处理
        Preprocess.lesson_data(config, semester)

    Preprocess.search_data(config)
