# coding=utf-8
import Config
import Common
import Student.database as dao


def update_list_data(config, version):
    tag_meaning = {
        "序号": "id",
        "学生学号": "code",
        "学生姓名": "name",
        "电子邮箱": "email",
        "班级名称": "class",
        "校区名称": "campus",
        "院系名称": "faculty",
    }

    Common.update_list_data(config, version, "学生列表", "student", tag_meaning, "xspk", 200)
    Common.merge_page_info(config, version, "学生列表", "student", dao.write_student_info)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update_list_data(_config, "2019-11-27")
