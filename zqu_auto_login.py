# -*- coding: utf-8 -*-
import datetime
import re
import wx
import frame
import login
import schedule
import os
from time import sleep
import platform
import threading
import logging
import sys

from config import file_abspath, location, logger, conf, config_file, is_running, init_log


# 创建mainWin类并传入my_win.MyFrame
class MainWin(frame.MyFrame):
    def getvalue(self, event):
        userid = self.userid.GetValue()
        password = self.password.GetValue()
        logout = self.check_logout.GetValue()
        logout_token = self.logout_token.GetValue()
        autorun = self.check_autorun.GetValue()
        return userid, password, logout, logout_token, autorun

    def open(self, event):
        if self.btn_open.GetLabel() == "开启":
            is_running = True
            self.btn_open.SetLabel("停止")
            userid, password, logout, logout_token, autorun = main_win.getvalue(self)
            conf.set('user', 'userid', value=userid)
            conf.set('user', 'password', password)
            conf.set('user', 'check_logout', str(logout))
            conf.set('user', 'logout_token', logout_token)
            conf.set('user', 'check_autorun', str(autorun))
            with open(config_file, 'w') as fw:  # 循环写入
                conf.write(fw)
            thread = MainThread(userid, password, autorun)
            thread.start()
        else:
            # os._exit(0)
            self.btn_open.SetLabel("开启")
            is_running = False
            logger.info('停止运行')


class MainThread(threading.Thread):
    def __init__(self, userid, password, check):  # 线程实例化时立即启动
        threading.Thread.__init__(self)
        self.userid = userid
        self.password = password
        self.check = check

    def run(self):  # 线程执行的代码
        self.auto_start()
        logger.debug('学号：' + self.userid + ' 密码:' + self.password)
        self.login_start()

    def auto_start(self):
        """
        开机启动
        """
        #######删除历史使用#######
        cmd = 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v AutoLogin /f '
        os.system(cmd)
        #########################
        name = 'AutoLogin_ZQU'  # 要添加的项值名称
        if 'Windows' in platform.system():
            try:
                if self.check:
                    cmd = 'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /t reg_sz /d "' + file_abspath + '" /f '
                    os.system(cmd)
                else:
                    cmd = 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /f '
                    os.system(cmd)
            except:
                logger.error('修改开机项失败')

    def login_start(self):
        """子线程要执行的代码"""
        logger.debug("第一次运行测试")
        login.main(self.userid, self.password)  # 第一次启动
        sleep(5)
        if conf.get('run', 'time_unit') == 'minutes':
            schedule.every(conf.getint('run', 'every_time')).minutes.do(login.main, self.userid, self.password)
        elif conf.get('run', 'time_unit') == 'seconds':
            schedule.every(conf.getint('run', 'every_time')).seconds.do(login.main, self.userid, self.password)  # 测试
        else:
            logger.critical('conf.ini配置错误：{}'.format(
                conf.getint('run', 'every_time'),
                conf.get('run', 'time_unit')
            ))
            sys.exit(1)
        while is_running:
            schedule.run_pending()
            sleep(1)
        schedule.clear()


"""
# 隐藏配置文件
def hideFile(file_abspath):
    if 'Windows' in platform.system():
        cmd = 'attrib +h "' + file_abspath + '"'
        os.system(cmd)
"""

if __name__ == '__main__':
    init_log()  # 初始化log文件
    # 下面是使用wxPython的固定用法
    app = wx.App()
    main_win = MainWin(None)
    main_win.Show()
    app.MainLoop()
