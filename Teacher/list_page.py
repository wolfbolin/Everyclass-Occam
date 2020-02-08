# coding=utf-8
import Config
import Common
import Teacher.database as dao


def update_list_data(config, version):
    tag_meaning = {
        "序号": "id",
        "教工号": "code",
        "姓名": "name",
        "职称": "title",
        "学历": "degree",
        "所属单位": "department",
        "所属教研室": "section",
    }

    Common.update_list_data(config, version, "教师列表", "teacher", tag_meaning, "jgpk", 200)
    Common.merge_page_info(config, version, "教师列表", "teacher", dao.write_teacher_info)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update_list_data(_config, "2019-11-27")
