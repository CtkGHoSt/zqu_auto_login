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
from logging.handlers import TimedRotatingFileHandler
import sys
import requests

from config import file_abspath, location, logger, conf, config_file, is_running


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
        global is_running
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
            thread = MainThread(
                userid=userid,
                password=password,
                check_logout=logout,
                check_autorun=autorun,
                btn_open=self.btn_open,
                logout_token=logout_token
            )
            thread.start()
        else:
            # os._exit(0)
            self.btn_open.SetLabel("开启")
            is_running = False
            logger.info('停止运行')


class MainThread(threading.Thread):
    def __init__(self, **argv):  # 线程实例化时立即启动
        threading.Thread.__init__(self)
        self.userid = argv['userid']
        self.password = argv['password']
        self.btn_open = argv['btn_open']
        self.logout_token = argv['logout_token']
        self.check_logout = argv['check_logout']
        self.check_autorun = argv['autorun']

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
                if self.check_autorun:
                    cmd = 'reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /t reg_sz /d "' + file_abspath + '" /f '
                    os.system(cmd)
                else:
                    cmd = 'reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v ' + name + ' /f '
                    os.system(cmd)
            except:
                logger.error('修改开机项失败')

    def login_start(self):
        """子线程要执行的代码"""

        def remote_logout():
            """
            远程下线
            """
            url = 'http://ovz.ctkghost.tk/logout?userid={}&token={}'.format(self.userid, self.logout_token)
            res = requests.get(url)
            if res.status_code == 200:
                global is_running
                is_running = False
                del_res = requests.delete(url)
                if del_res.status_code == 200:
                    login.logout_campus_network()
                    logger.warning('远程下线成功')
                else:
                    logger.error('远程下线失败 status code:{}'.format(del_res.status_code))

        logger.debug("第一次运行测试")
        login.main(self.userid, self.password)  # 第一次启动
        sleep(5)
        logout_token = conf.get('user', 'logout_token')
        # 远程下线
        if self.check_logout and self.logout_token:
            schedule.every(10).seconds.do(remote_logout)
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
        global is_running
        while is_running:
            schedule.run_pending()
            sleep(1)
        schedule.clear()
        self.btn_open.SetLabel("开启")


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
