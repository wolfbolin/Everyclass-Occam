# coding=utf-8
import Config
import Common
import Course.database as dao


def update_list_data(config, version):
    tag_meaning = {
        "序号": "id",
        "课程号": "code",
        "课程名称": "name",
        "课程大类": "type",
        "开课单位": "faculty",
    }

    Common.fetch_list_data(config, version, "课程列表", "course", tag_meaning, "kcpx", 100)
    Common.merge_page_info(config, version, "课程列表", "course", dao.write_room_info)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update_list_data(_config, "2019-11-27")
