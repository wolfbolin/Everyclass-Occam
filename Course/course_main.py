# coding=utf-8
import Config
import Common
import Course.database as dao


def update(config, semester, version):
    # 更新全体名单
    tag_meaning = {
        "序号": "id",
        "课程号": "code",
        "课程名称": "name",
        "课程大类": "type",
        "开课单位": "department",
    }
    if Common.fetch_list_data(config, "课程列表", "course_list", tag_meaning, "kcmd", 100):
        Common.update_page_info(config, "课程列表", "course_list", dao.write_course_info)

    # 更新活跃教室
    active_list = Common.fetch_active_list(config, version, "可用课程", "act_course", "kclb", semester)
    Common.update_active_list(config, "可用课程", "act_course", "course", semester, active_list)

    # 更新教室课表
    Common.fetch_class_table_oc(config, version, "课程课表", "course_table", "course", "kckb", semester, active_list)
    Common.update_table_info_oc(config, version, "课程课表", "course_table", "course", semester)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    main(_config, "2019-2020-1", "2020-02-16")
