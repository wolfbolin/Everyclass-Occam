# coding=utf-8
import Config
import Common
import Room.database as dao


def update_list_data(config, version):
    tag_meaning = {
        "序号": "id",
        "教室编号": "code",
        "教室名称": "name",
        "教室类型": "type",
        "座位数": "seat",
        "有效座位": "effect_seat",
        "考试座位数": "exam_seat",
        "所在校区": "campus",
        "所在教学楼": "building",
    }

    Common.fetch_list_data(config, version, "教室列表", "room", tag_meaning, "jspk", 200)
    Common.merge_page_info(config, version, "教室列表", "room", dao.write_room_info)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update_list_data(_config, "2019-11-27")
