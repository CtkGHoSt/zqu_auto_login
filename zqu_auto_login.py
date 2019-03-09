# -*- coding: utf-8 -*-
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


from config import file_abspath, location, logger, conf

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
            conf.set('user', 'userid', value=userid)
            conf.set('user', 'password', password)
            conf.set('user', 'check', str(check))
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

    def run(self):  # 线程执行的代码
        self.auto_start()
        logger.info('学号：' + self.userid + ' 密码:' + self.password)
        self.login_start()
    
    def auto_start(self):
        '''
        开机启动
        '''
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
        '''子线程要执行的代码'''
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
        while 1:
            schedule.run_pending()
            sleep(1)

def initLog():
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


# 隐藏配置文件
def hideFile(file_abspath):
    if 'Windows' in platform.system():
        cmd = 'attrib +h "' + file_abspath + '"'
        os.system(cmd)


if __name__ == '__main__':
    # 初始化程序
    initLog()  # 初始化log文件
    # 下面是使用wxPython的固定用法
    app = wx.App()
    main_win = mainWin(None)
    main_win.Show()
    app.MainLoop()
