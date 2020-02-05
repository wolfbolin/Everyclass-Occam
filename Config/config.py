# coding=utf-8
import os
import Util
import configparser


# 读取配置文件
def load_config(config_path):
    run_env = 'develop'
    if 'SERVICE_ENV' in os.environ:
        run_env = os.environ['SERVICE_ENV']

    Util.print_yellow("Load config file [%s].ini" % run_env)
    config_file = os.path.join(config_path, "%s.ini" % run_env)
    Util.print_white(os.path.abspath(config_file))

    if os.path.isfile(config_file):
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        app_config = dict()
        for section in config.sections():
            app_config[section] = dict(config.items(section))

        return app_config
    else:
        Util.print_red("Config not exist")
        exit()


if __name__ == '__main__':
    _config = load_config("./")
    print(_config)
