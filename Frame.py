import wx  # 引入wx模块<br>
import os
from configparser import ConfigParser
import sys
import wx.adv

TITLE = "肇庆学院校园网自动登录"
ICON = "icon.ico"  # 图标地址

class MyTaskBarIcon(wx.adv.TaskBarIcon):
    ID_EXIT = wx.NewId()  # 菜单选项“退出”的ID
    ID_SHOW_WEB = wx.NewId()  # 菜单选项“显示页面”的ID

    def __init__(self,frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        # self.TITLE = "肇庆学院校园网自动登录"
        self.SetIcon(wx.Icon(ICON), TITLE)  # 设置图标和标题
        self.Bind(wx.EVT_MENU, self.onExit, id=self.ID_EXIT)  # 绑定“退出”选项的点击事件
        self.Bind(wx.EVT_MENU, self.onShow, id=self.ID_SHOW_WEB)  # 绑定“显示页面”选项的点击事件
        # self.Bind(wx.EVT_COMMAND_LEFT_DCLICK, self.OnTaskBarLeftDClick)  # 绑定“显示页面”选项的点击事件

    # “退出”选项的事件处理器
    def onExit(self, event):
        wx.Exit()

    # “显示页面”选项的事件处理器
    def onShow(self, event):
        self.frame.Show(True)
        self.frame.Raise()

    # 双击显示选项的事件处理器
    def OnTaskBarLeftDClick(self, event):
        pass
        # if self.frame.IsIconized():
        #     self.frame.Iconize(False)
        # if not self.frame.IsShown():
        #     self.frame.Show(True)
        # self.frame.Raise()

    # 创建菜单选项
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_SHOW_WEB, '进入程序')
        menu.Append(self.ID_EXIT, '退出')
        return menu



class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=TITLE, pos=wx.DefaultPosition,
                          size=wx.Size(320, 174),
                          style=wx.DEFAULT_FRAME_STYLE |
                                wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.taskBarIcon=MyTaskBarIcon(self)#显示系统托盘图标
        self.SetMaxSize((320, 174))  # 固定窗口
        self.SetMinSize((320, 174))
        gSizer = wx.GridSizer(0, 2, 0, 0)
        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"学号", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        gSizer.Add(self.m_staticText2, 0, wx.ALL, 5)
        self.userid = wx.TextCtrl(self, wx.ID_ANY, u"2016241314xx", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer.Add(self.userid, 0, wx.ALL, 5)
        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"密码(电信8位;移动6位)", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        gSizer.Add(self.m_staticText1, 0, wx.ALL, 5)
        self.password = wx.TextCtrl(self, wx.ID_ANY, u"xxxxxxxx", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer.Add(self.password, 0, wx.ALL, 5)
        self.check_start = wx.CheckBox(self, wx.ID_ANY, u"开机自启", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer.Add(self.check_start, 0, wx.ALL, 5)
        self.btn_open = wx.Button(self, wx.ID_ANY, u"开启", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer.Add(self.btn_open, 0, wx.ALL, 5)

        self.SetSizer(gSizer)
        self.Layout()
        self.Centre(wx.BOTH)

        self.config_file = os.path.dirname(os.path.abspath(sys.argv[0])) + "/conf.ini"
        conf = ConfigParser()
        conf.read(self.config_file, encoding='utf-8')
        # 获取数据
        if os.path.exists(self.config_file):
            userid = conf.get('user', 'userid')
            password = conf.get('user', 'password')
            check = conf.get('user', 'check')

            self.userid.SetValue(userid)
            self.password.SetValue(password)
            if check == "True":
                self.check_start.SetValue(True)


            # 绑定按钮的单击事件
        self.Bind(wx.EVT_BUTTON, self.open, self.btn_open)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy) # 窗口最小化时，调用OnIconfiy,注意Wx窗体上的最小化按钮，触发的事件是 wx.EVT_ICONIZE,而根本就没有定义什么wx.EVT_MINIMIZE,但是最大化，有个wx.EVT_MAXIMIZE。
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def open(self, event):
        event.Skip()

    def OnIconfiy(self, event):
        self.Hide()
        self.Iconize(False)

    def OnClose(self, event):
        self.taskBarIcon.Destroy()
        self.Destroy()

    def __del__(self):
        pass

