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


    def run(self):  # 线程执行的代码
        logging.info('学号：' + self.userid + ' 密码:' + self.password)
        writeConfig(self)#写入数据到配置文件
        readConfig(self)

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
    date = "[user]\n" \
           "userid =" + self.userid + "\n" \
            "password =" + self.password + "\n" \
            "check ="+ str(self.check) +"\n\n"\
           "[run]\n" \
           "time_unit = minutes\n" \
           "every_time = 5\n" \
           "begin_time = 07:00\n" \
           "end_time = 23:59\n" \
            "log_level = debug"
    # if os.path.exists(config_file):
    #     os.remove(config_file)
    f = open(self.config_file, 'w')
    f.write(date)
    f.close()
    # hideFile(config_file)

def readConfig(self):
    self.conf.read(self.config_file, encoding='utf-8')
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
        # filename='run.log',
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
def autostart(filePath):
    if 'Windows' in platform.system():
        cmd = 'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v winrar /t reg_sz /d "' + filePath + '" /f '
        os.system(cmd)


# 子线程要执行的代码
def login(self):
    #第一次登陆
    auto_login.test(self)
    sleep(5)
    schedule.every(5).minutes.do(auto_login.test)
    # schedule.every(5).seconds.do(auto_login.test,self)#测试
    while (1):
        schedule.run_pending()
        sleep(5)


if __name__ == '__main__':
    # 下面是使用wxPython的固定用法
    app = wx.App()
    main_win = mainWin(None)
    main_win.Show()
    app.MainLoop()
