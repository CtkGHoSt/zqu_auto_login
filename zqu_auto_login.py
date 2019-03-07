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
import logging,logging.handlers
import sys

filePath = os.path.abspath(sys.argv[0])  # 绝对当前exe所在目录地址
location = os.path.dirname(filePath)# 绝对当前exe所在文件夹目录地址

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
        self.log_level = logging.INFO
        self.begin_time = ""
        self.end_time = ""

    def run(self):  # 线程执行的代码
        writeConfig(self)
        # readConfig(self)
        autostart(self)
        logging.info('学号：' + self.userid + ' 密码:' + self.password)
        loginstart(self)

def init():
    initConfig()  # 初始化数据到配置文件
    initLog()  # 初始化log文件

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
               "log_level = 10\n" \
                "//ERROR = 40,WARNING = 30,INFO = 20,DEBUG = 10,NOTSET = 0"
        f = open(location + "\conf.ini", 'w')
        f.write(date)
        f.close()

def initLog():
    conf = ConfigParser()
    conf.read(location + "\conf.ini", encoding='utf-8')
    # 获取开始时间和结束时间
    begin_time = conf.get('run', 'begin_time')
    end_time = conf.get('run', 'end_time')
    log_level = conf.get('run', 'log_level')
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
    logger = logging.getLogger("run")
    logger.setLevel(int(log_level))
    format = "[%(asctime)s] - %(levelname)s - %(module)s: %(message)s"
    # 结果是每7天生成一个日志文件，保留最近10次的日志文件
    # when参数可以设置S M H D,分别是秒、分、小时、天分割，也可以按周几分割，也可以凌晨分割
    file_run_log = rf_handler = logging.handlers.TimedRotatingFileHandler(run_log, when='S', interval=7,
                                                                          backupCount=10,
                                                                          atTime=datetime.time(0, 0, 0, 0))
    # 删除日志文件
    file_run_log.suffix = "%Y-%m-%d_%H-%M.log"
    file_run_log.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
    file_run_log.setLevel(level=logging.INFO)
    file_run_log.setFormatter(logging.Formatter(format))
    logger.addHandler(file_run_log)
    # 既输出到文件，又打印到terminal
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

# 写入配置文件
def writeConfig(self):
    self.conf.read(self.config_file, encoding='utf-8')
    self.conf.set('user', 'userid', value=self.userid)
    self.conf.set('user', 'password', self.password)
    self.conf.set('user', 'check', str(self.check))
    with open(self.config_file, 'w') as fw:  # 循环写入
        self.conf.write(fw)

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
            logging.error('修改开机项失败')


# 子线程要执行的代码
def loginstart(self):
    logging.debug("第一次运行测试")
    login.test(self)  # 第一次启动
    sleep(5)
    if self.conf.get('run', 'time_unit') == 'minutes':
        schedule.every(self.conf.getint('run', 'every_time')).minutes.do(login.test, self)
    elif self.conf.get('run', 'time_unit') == 'seconds':
        schedule.every(self.conf.getint('run', 'every_time')).seconds.do(login.test, self)  # 测试
    else:
        logging.critical('conf.ini配置错误：{}'.format(
            self.conf.getint('run', 'every_time'),
            self.conf.get('run', 'time_unit')
        ))
        sys.exit(1)
    while 1:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':

    #初始化程序
    init()
    # 下面是使用wxPython的固定用法
    app = wx.App()
    main_win = mainWin(None)
    main_win.Show()
    app.MainLoop()
