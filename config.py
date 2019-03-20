# -*- coding: utf-8 -*-
import os
import sys
import logging

from configparser import ConfigParser

# 运行状态
is_running = False

# 路径
file_abspath = os.path.abspath(sys.argv[0])  # exe所在目录地址
location = os.path.dirname(file_abspath)  # exe所在文件夹目录地址
config_file = location + "\conf.ini"

# log
logger = logging.getLogger("mylogger")

#常量名称
auto_run_name = 'AutoLogin_ZQU'  # 要添加的项值名称


# conf.ini
def load_conf():
    def initConfig():
        if not os.path.exists(location + "\log"):
            os.mkdir("log")
        if not os.path.exists(location + "\conf.ini"):
            date = "[user]\n" \
                   "userid = 2016241314xx\n" \
                   "password = xxxxxxxx\n" \
                   "check_logout = False\n" \
                   "logout_token = xxxxx\n" \
                   "check_autorun = True\n\n" \
                   "[run]\n" \
                   "time_unit = minutes\n" \
                   "every_time = 5\n" \
                   "begin_time = 07:00\n" \
                   "end_time = 23:59\n" \
                   "log_level = debug\n" \
                   "logout_token = \n"
            f = open(location + "\conf.ini", 'w')
            f.write(date)
            f.close()

    initConfig()
    conf = ConfigParser()
    conf.read(config_file, encoding='utf-8')
    return conf


conf = load_conf()
