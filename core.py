import wx  # 引入wx模块<br>
import Frame
import auto_login
import schedule
import os
from time import sleep
import platform
import threading

class TestThread(threading.Thread):
    def __init__(self,userid, password, check):  # 线程实例化时立即启动
        threading.Thread.__init__(self)
        self.userid =userid
        self.password = password
        self.check = check

    def run(self):  # 线程执行的代码
        print(self.userid + self.password)
        writeConfig(self.userid,self.password,self.check)#写入数据到配置文件
        auto_login.test()
        sleep(5)
        login()

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
def writeConfig(userid,password,check):
    config_file = "conf.ini"
    date = "[user]\n" \
           "userid =" + userid + "\n" \
            "password =" + password + "\n" \
            "check ="+ str(check) +"\n\n"\
           "[run]\n" \
           "time_unit = minutes\n" \
           "every_time = 5\n" \
           "begin_time = 07:00\n" \
           "end_time = 23:59\n" \
            "log_level = debug"
    if os.path.exists(config_file):
        os.remove(config_file)
    f = open(config_file, 'w')
    f.write(date)
    f.close()
    hideFile(config_file)

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
def login():
    schedule.every(5).minutes.do(auto_login.test)
    while (1):
        schedule.run_pending()
        sleep(5)


if __name__ == '__main__':
    # 下面是使用wxPython的固定用法
    app = wx.PySimpleApp()
    main_win = mainWin(None)
    main_win.Show()
    print("test1")
    app.MainLoop()
