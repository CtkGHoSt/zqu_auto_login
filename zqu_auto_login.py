import datetime
import re
import wx  # 引入wx模块
import Frame
import login
import schedule
import os
from time import sleep
import platform
import threading
from configparser import ConfigParser
import logging
from logging.handlers import TimedRotatingFileHandler
import sys

filePath = os.path.abspath(sys.argv[0])  # exe所在目录地址
location = os.path.dirname(filePath)  # exe所在文件夹目录地址
logger = logging.getLogger("mylogger")


# 创建mainWin类并传入my_win.MyFrame
class mainWin(Frame.MyFrame):
    def GetValue(self, event):
        userid = self.userid.GetValue()
        password = self.password.GetValue()
        check = self.check_start.GetValue()
        return userid, password, check

    def open(self, event):
        if self.btn_open.GetLabel() == "开启":
            self.btn_open.SetLabel("关闭")
            userid, password, check = main_win.GetValue(self)
            thread = MainThread(userid, password, check)
            thread.start()
        else:
            os._exit(0)


class MainThread(threading.Thread):
    def __init__(self, userid, password, check):  # 线程实例化时立即启动
        threading.Thread.__init__(self)
        self.userid = userid
        self.password = password
        self.check = check
        self.config_file = location + "\conf.ini"
        self.conf = ConfigParser()
        self.begin_time = ""
        self.end_time = ""
        self.logger = logger
        self.time_unit = ""

    def run(self):  # 线程执行的代码
        Config(self)
        autostart(self)
        self.logger.info('学号：' + self.userid + ' 密码:' + self.password)
        loginstart(self)


def initConfig():
    if not os.path.exists(location + "\log"):
        os.mkdir("log")
    if not os.path.exists(location + "\conf.ini"):
        date = "[user]\n" \
               "userid = 2016241314xx\n" \
               "password = xxxxxxxx\n" \
               "check = True\n\n" \
               "[run]\n" \
               "time_unit = minutes\n" \
               "every_time = 5\n" \
               "begin_time = 07:00\n" \
               "end_time = 23:59\n" \
               "log_level = debug\n"
        f = open(location + "\conf.ini", 'w')
        f.write(date)
        f.close()


def initLog():
    global log_level
    conf = ConfigParser()
    conf.read(location + "\conf.ini", encoding='utf-8')
    # 获取开始时间和结束时间

    level = conf.get('run', 'log_level')
    if level == 'info':
        log_level = logging.INFO
    elif level == 'warning':
        log_level = logging.WARNING
    else:
        log_level = logging.DEBUG
    """
    log日志的简单应用
    logging.basicConfig(
        format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=log_level,
        handlers=[logging.FileHandler(location + "\\run.log"), logging.StreamHandler()]
    )
    """
    """
    log日志，按时间分割，清理过时日志
    """
    run_log = location + "\\log\\run.log"
    logger.setLevel(log_level)
    format =logging.Formatter("[%(asctime)s]-%(levelname)-6s %(module)s:%(lineno)d - %(message)s","%m-%d %H:%M:%S")
    """
    切割日志
    结果是每1天生成一个日志文件，保留最近10次的日志文件,MIDNIGHT
    when参数可以设置S M H D,分别是秒、分、小时、天分割，也可以按周几分割，也可以凌晨分割
    """
    handler = TimedRotatingFileHandler(run_log, when='MIDNIGHT', interval=1,
                                                             backupCount=30,encoding='utf-8',
                                                             atTime=datetime.time(0, 0, 0, 0))
    handler.suffix = "%Y-%m-%d.log"#切割后的日志设置后缀
    handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
    handler.setLevel(log_level)
    handler.setFormatter(format)
    logger.addHandler(handler)
    # 既输出到文件，又打印到terminal
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(format)
    logging.getLogger().addHandler(console)


    # logger.debug("debug")
    # logger.info("info")

# 配置文件
def Config(self):
    self.conf.read(self.config_file, encoding='utf-8')
    self.conf.set('user', 'userid', value=self.userid)
    self.conf.set('user', 'password', self.password)
    self.conf.set('user', 'check', str(self.check))
    with open(self.config_file, 'w') as fw:  # 循环写入
        self.conf.write(fw)
    # 读取
    self.begin_time = self.conf.get('run', 'begin_time')
    self.end_time = self.conf.get('run', 'end_time')
    self.time_unit = self.conf.get('run', 'time_unit')


# 隐藏配置文件
def hideFile(filePath):
    if 'Windows' in platform.system():
        cmd = 'attrib +h "' + filePath + '"'
        os.system(cmd)


# 开机自启
def autostart(self):
    #######删除历史使用#######
    cmd = 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v AutoLogin /f '
    os.system(cmd)
    #########################
    name = 'AutoLogin_ZQU'  # 要添加的项值名称
    if 'Windows' in platform.system():
        try:
            if self.check:
                cmd = 'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /t reg_sz /d "' + filePath + '" /f '
                os.system(cmd)
            else:
                cmd = 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /f '
                os.system(cmd)
        except:
            self.logger.error('修改开机项失败')


# 子线程要执行的代码
def loginstart(self):
    self.logger.debug("第一次运行测试")
    login.main(self)  # 第一次启动
    sleep(5)
    if self.time_unit == 'minutes':
        schedule.every(self.conf.getint('run', 'every_time')).minutes.do(login.main, self)
    elif self.time_unit == 'seconds':
        schedule.every(self.conf.getint('run', 'every_time')).seconds.do(login.main, self)  # 测试
    else:
        self.logger.critical('conf.ini配置错误：{}'.format(
            self.conf.getint('run', 'every_time'),
            self.conf.get('run', 'time_unit')
        ))
        sys.exit(1)
    while 1:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    # 初始化程序
    initConfig()  # 初始化数据到配置文件
    initLog()  # 初始化log文件
    # 下面是使用wxPython的固定用法
    app = wx.App()
    main_win = mainWin(None)
    main_win.Show()
    app.MainLoop()
