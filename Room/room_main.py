# coding=utf-8
import Config
import Common
import Room.database as dao


def main(config, semester, version):
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
    if Common.fetch_list_data(config, version, "教室列表", "room_list", tag_meaning, "jsmd", 200):
        Common.merge_page_info(config, version, "教室列表", "room_list", dao.write_room_info)

    # 更新活跃教室
    active_list = Common.fetch_active_list(config, version, "可用教室", "act_room", "jslb", semester)

    # 更新教室课表
    Common.fetch_class_table(_config, version, "教室课表", "room_table", "jskb", semester, active_list)
    Common.merge_table_info(_config, version, "教室课表", "room_table", "room")


if __name__ == "__main__":
    _config = Config.load_config("../Config")
    main(_config, "2019-2020-1", "2020-02-16")
