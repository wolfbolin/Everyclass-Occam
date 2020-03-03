# coding=utf-8
import Util
import Room
import Config
import Course
import Student
import Teacher
import Preprocess

if __name__ == "__main__":
    config = Config.load_config("./Config")

    # 重新计算所有学期数据
    for semester in config["schedule"]:
        Util.print_blue("当前计算学期: %s" % semester)
        # 重新计算对象信息
        Room.update(config, semester, config["schedule"][semester])
        Course.update(config, semester, config["schedule"][semester])
        Student.update(config, semester, config["schedule"][semester])
        Teacher.update(config, semester, config["schedule"][semester])

        # 重新完成数据预处理
        Preprocess.lesson_data_oc(config, semester)

    Preprocess.search_data(config)
