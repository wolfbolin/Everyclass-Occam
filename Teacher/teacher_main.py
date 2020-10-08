# coding=utf-8
import Config
import Common
import Teacher.database as dao


def update(config, semester, version):
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
    if Common.fetch_list_data(config, "教师列表", "teacher_list", tag_meaning, "jgmd", 200):
        Common.update_page_info(config, "教师列表", "teacher_list", dao.write_teacher_info)

    # 更新活跃教室
    active_list = Common.fetch_active_list(config, version, "可用教师", "act_teacher", "jglb", semester)
    Common.update_active_list(config, "可用教师", "act_teacher", "teacher", semester, active_list)

    # 更新教室课表
    Common.fetch_class_table_oc(config, version, "教师课表", "teacher_table", "teacher", "jgkb", semester, active_list)
    Common.update_table_info_oc(config, version, "教师课表", "teacher_table", "teacher", semester)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update(_config, "2020-2021-1", "2020-2021-10-05")
