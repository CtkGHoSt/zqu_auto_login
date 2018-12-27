import wx  # 引入wx模块<br>
import Frame
import auto_login
import schedule
import os
from time import sleep
import platform
import threading
from configparser import ConfigParser
import logging
import sys

class TestThread(threading.Thread):
    def __init__(self,userid, password, check):  # 线程实例化时立即启动
        threading.Thread.__init__(self)
        self.userid =userid
        self.password = password
        self.check = check
        self.config_file = "conf.ini"
        self.conf = ConfigParser()
        self.log_level = logging.INFO
        self.begin_time = ""
        self.end_time = ""

    def run(self):  # 线程执行的代码
        writeConfig(self)#写入数据到配置文件
        readConfig(self)
        autostart(self)
        logging.info('学号：' + self.userid + ' 密码:' + self.password)
        login(self)

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
            thread = TestThread(userid, password, check)
            thread.start()
        else:
            os._exit(0)

# 写入配置文件
def writeConfig(self):
    if not os.path.exists(self.config_file):
        date = "[user]\n" \
               "userid =" + self.userid + "\n" \
               "password =" + self.password + "\n" \
               "check =" + str(self.check) + "\n\n" \
               "[run]\n" \
               "time_unit = minutes\n" \
               "every_time = 5\n" \
               "begin_time = 07:00\n" \
               "end_time = 23:59\n" \
               "log_level = debug"
        f = open(self.config_file, 'w')
        f.write(date)
        f.close()
    else:
        self.conf.set('user', 'userid', self.userid)
        self.conf.set('user', 'password', self.password)
        self.conf.set('user', 'check', str(self.check))


def readConfig(self):
    self.conf.read(self.config_file, encoding='utf-8')
    #获取开始时间和结束时间
    self.begin_time = self.conf.get('run', 'begin_time')
    self.end_time = self.conf.get('run', 'end_time')

    if self.conf.get('run', 'log_level') == 'debug':
        self.log_level = logging.DEBUG
    elif self.conf.get('run', 'log_level') == 'info':
        self.log_level = logging.INFO
    elif self.conf.get('run', 'log_level') == 'warning':
        self.log_level = logging.WARNING
    else:
        print('log level error.')
        sys.exit(1)
    logging.basicConfig(
        format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=self.log_level,
        handlers=[logging.FileHandler("run.log"), logging.StreamHandler()]
    )

# 隐藏配置文件
def hideFile(filePath):
    if 'Windows' in platform.system():
        cmd = 'attrib +h "' + filePath + '"'
        os.system(cmd)

# 开机自启
def autostart(self):
    name = 'AutoLogin'  # 要添加的项值名称
    filePath = os.path.realpath(__file__)  # 要添加的exe路径
    if 'Windows' in platform.system():
        try:
            if self.check:
                cmd = 'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + '/t reg_sz /d "' + filePath + '" /f '
                os.system(cmd)
            else:
                cmd = 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /f '
                os.system(cmd)
        except:
            logging.error('修改开机项失败')

# 子线程要执行的代码
def login(self):
    auto_login.test(self)#第一次启动
    sleep(5)
    if self.conf.get('run', 'time_unit') == 'minutes':
        schedule.every(self.conf.getint('run', 'every_time')).minutes.do(auto_login.test,self)
    elif self.conf.get('run', 'time_unit') == 'seconds':
        schedule.every(self.conf.getint('run', 'every_time')).seconds.do(auto_login.test,self)#测试
    else:
        logging.critical('conf.ini配置错误：{}'.format(
            self.conf.getint('run', 'every_time'),
            self.conf.get('run', 'time_unit')
        ))
        sys.exit(1)
    while (1):
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    # 下面是使用wxPython的固定用法
    app = wx.App()
    main_win = mainWin(None)
    main_win.Show()
    app.MainLoop()
