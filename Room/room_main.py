# coding=utf-8
import Config
import Common
import Room.database as dao


def update(config, semester, version):
    # 更新全体名单
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
    if Common.fetch_list_data(config, "教室列表", "room_list", tag_meaning, "jsmd", 200):
        Common.update_page_info(config, "教室列表", "room_list", dao.write_room_info)

    # 更新活跃教室
    active_list = Common.fetch_active_list(config, version, "可用教室", "act_room", "jslb", semester)
    Common.update_active_list(config, "可用教室", "act_room", "room", semester, active_list)

    # 更新教室课表
    Common.fetch_class_table(config, version, "教室课表", "room_table", "room", "jskb", semester, active_list)
    Common.update_table_info(config, version, "教室课表", "room_table", "room", semester)


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    update(_config, "2019-2020-1", "2020-02-16")
