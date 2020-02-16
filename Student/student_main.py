# coding=utf-8
import Config
import Common
import Student.database as dao


def main(config, semester, version):
    # 更新全体名单
    tag_meaning = {
        "序号": "id",
        "学生学号": "code",
        "学生姓名": "name",
        "电子邮箱": "email",
        "班级名称": "class",
        "校区名称": "campus",
        "院系名称": "faculty",
    }
    if Common.fetch_list_data(config, version, "学生列表", "student_list", tag_meaning, "xsmd", 200):
        Common.merge_page_info(config, version, "学生列表", "student_list", dao.write_student_info)

    # 更新活跃教室
    active_list = Common.fetch_active_list(config, version, "可用学生", "act_student", "xslb", semester)

    # 更新教室课表
    Common.fetch_class_table(_config, version, "学生课表", "student_table", "xskb", semester, active_list)
    Common.merge_table_info(_config, version, "学生课表", "student_table", "student")


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    main(_config, "2019-2020-1", "2020-02-16")
