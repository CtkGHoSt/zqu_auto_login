# -*- coding: utf-8 -*-
import os
import sys
import logging
import datetime
import re

from logging.handlers import TimedRotatingFileHandler
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

def init_log():
    level = conf.get('run', 'log_level')
    if level == 'info':
        log_level = logging.INFO
    elif level == 'warning':
        log_level = logging.WARNING
    else:
        log_level = logging.DEBUG
    """
    log日志，按时间分割，清理过时日志
    """
    run_log = location + "\\log\\run.log"
    logger.setLevel(log_level)
    format = logging.Formatter("[%(asctime)s]-%(levelname)-6s %(module)s:%(lineno)d - %(message)s", "%m-%d %H:%M:%S")
    """
    切割日志
    结果是每1天生成一个日志文件，保留最近10次的日志文件,MIDNIGHT
    when参数可以设置S M H D,分别是秒、分、小时、天分割，也可以按周几分割，也可以凌晨分割
    """
    handler = TimedRotatingFileHandler(run_log, when='MIDNIGHT', interval=1,
                                       backupCount=30, encoding='utf-8',
                                       atTime=datetime.time(0, 0, 0, 0))
    handler.suffix = "%Y-%m-%d.log"  # 切割后的日志设置后缀
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    handler.setLevel(log_level)
    handler.setFormatter(format)
    logger.addHandler(handler)
    # 既输出到文件，又打印到terminal
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(format)
    logging.getLogger().addHandler(console)
