# coding=utf-8
import os
import Util
import Config


def test_task(arg):
    print(os.getpid())


if __name__ == '__main__':
    # 读取配置文件
    run_env = 'development'
    if 'SERVICE_ENV' in os.environ and os.environ['SERVICE_ENV'] in Config.configs:
        run_env = os.environ['SERVICE_ENV']
    run_config = Config.configs[run_env]

    result = Util.multiprocess(run_config, test_task, Util.simple_multithread, ['1', '1', '1', '1', '1', '1', ], None)
