import wx  # 引入wx模块<br>
import os
from configparser import ConfigParser
import sys
class MyFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="肇庆学院校园网自动登录", pos=wx.DefaultPosition,
                          size=wx.Size(320, 174),
                          style=wx.DEFAULT_FRAME_STYLE |
                                wx.TAB_TRAVERSAL)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetMaxSize((320, 174))#固定窗口
        self.SetMinSize((320, 174))
        gSizer = wx.GridSizer(0, 2, 0, 0)
        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"学号", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        gSizer.Add(self.m_staticText2, 0, wx.ALL, 5)
        self.userid = wx.TextCtrl(self, wx.ID_ANY, u"2016241314xx", wx.DefaultPosition, wx.DefaultSize, 0)
        gSizer.Add(self.userid, 0, wx.ALL, 5)
        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"密码(8位)", wx.DefaultPosition, wx.DefaultSize, 0)
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


        
        self.config_file = os.path.dirname(os.path.abspath(sys.argv[0]))+"/conf.ini"
        conf = ConfigParser()
        conf.read(self.config_file , encoding='utf-8')
        # 获取数据
        if os.path.exists(self.config_file):
            userid = conf.get('user', 'userid')
            password = conf.get('user', 'password')
            check=conf.get('user','check')

            self.userid.SetValue(userid)
            self.password.SetValue(password)
            if check=="True":
                self.check_start.SetValue(True)

        # 绑定按钮的单击事件
        self.Bind(wx.EVT_BUTTON, self.open, self.btn_open)

    def __del__(self):
        pass

    def open(self, event ):
        event.Skip()
