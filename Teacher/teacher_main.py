# coding=utf-8
import Config
import Common
import Teacher.database as dao


def main(config, semester, version):
    # 更新全体名单
    tag_meaning = {
        "序号": "id",
        "教工号": "code",
        "姓名": "name",
        "职称": "title",
        "学历": "degree",
        "所属单位": "department",
        "所属教研室": "section",
    }
    if Common.fetch_list_data(config, version, "教师列表", "teacher_list", tag_meaning, "jgmd", 200):
        Common.merge_page_info(config, version, "教师列表", "teacher_list", dao.write_teacher_info)

    # 更新活跃教室
    active_list = Common.fetch_active_list(config, version, "可用教师", "act_teacher", "jglb", semester)

    # 更新教室课表
    Common.fetch_class_table(_config, version, "教师课表", "teacher_table", "jgkb", semester, active_list)
    Common.merge_table_info(_config, version, "教师课表", "teacher_table", "teacher")


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    main(_config, "2019-2020-1", "2020-02-16")
