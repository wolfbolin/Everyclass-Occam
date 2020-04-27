# coding=utf-8
import os
import Util
import Config
import Common


def main(config, folder, semester):
    conn = Util.mysql_conn(config, "mysql-origin")
    transform_list(conn, folder, "teacher", semester)
    transform_list(conn, folder, "student", semester)
    transform_table(conn, folder, "teacher", semester)
    transform_table(conn, folder, "student", semester)


def transform_list(conn, folder, group, semester):
    file = open("{}/{}_list".format(folder, group), encoding="utf-8")
    file_data = file.read()
    Common.write_json_data(conn, "act_{}".format(group), semester, 1, file_data)


def transform_table(conn, folder, group, semester):
    file_list = os.listdir("{}/{}_html".format(folder, group))
    for i, file_name in enumerate(file_list):
        code = file_name.replace("#", "*")
        file = open("{}/{}_html/{}".format(folder, group, file_name), encoding="utf-8")
        file_data = file.read()
        Common.write_html_data(conn, "{}_table".format(group), semester, code, file_data)
        Util.process_bar(i + 1, len(file_list), "{}_table  ".format(group))


if __name__ == "__main__":
    _folder = input("folder: ")
    _semester = input("semester: ")
    _config = Config.load_config("./Config")
    main(_config, _folder, _semester)
