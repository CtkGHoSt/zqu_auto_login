# 肇庆学院电信wifi校园网自动登录 [![](https://img.shields.io/badge/release-1.0.2-brightgreen.svg)](https://github.com/CtkGHoSt/zqu_auto_login/releases)


### by ctkghost chiihero
---
![](https://s1.ax1x.com/2018/12/27/FRr06H.png)     
在可验证的时间段内每隔一段时间判断一次状态，在非联网状态下登录校园局域网和电信校园网
> * ###直接双击执行zqu_auto_login.exe，输入学号密码，点击开启即可
>* 文件偏大原因在于用python打包运行环境而成，运行后占用资源非常小

---
### 说明

若需要修改conf.ini文件,需要运行一次zqu_auto_login.exe文件(适用于需要自定义用户)\
conf.ini ：
```
[user]
userid = 12位学号
password = 移动输入6位密码或电信8位密码

[run]
time_unit = minutes 每次间隔的时间单位 （minutes/seconds）
every_time = 10 每次间隔时间
begin_time = 07:00 允许登录时间
end_time = 23:59 不允许登录时间
log_level = debug 日志级别输出 （debug/info/warning）
# 早上7点到晚上23点59分内，每隔10分钟执行 判断是否需要登录校园网操作

```

>
已知bug：   
远程下线可能导致再次登录  
验证码获取文件错误导致自动下线     
…   
>
todo：   
修复bug    
…

> v1.0.2 更新    
使用分割日志，并且定时清除
重构代码
修复无法退出bug
添加周末凌晨运行

> v1.0.1 更新    
添加最小化任务栏模式

> v0.9.9 更新  
修复已知bug\
去除code文件夹内的基准图片

> v0.1.1 更新    
修复无法开机自启\
关闭dos调试窗口

> v0.1.0 更新    
更新了windows ui\
修复了无数个bug

> v0.0.3 更新    
修复了auto login \
1获取重定向连接异常

> v0.0.2 更新    
更新log输出\
修复无数个bug

