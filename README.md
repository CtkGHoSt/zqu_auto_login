# 肇庆学院电信wifi校园网自动登录 v0.1.0 
### by ctkghost
---   


在可验证的时间段内每隔一段时间判断一次状态，在非联网状态下登录校园局域网和电信校园网

> * 源码在source文件夹下
> * code文件夹下是用于验证码识别的图片
> * 执行方式：直接打开core.exe
> * ~~执行方式：当前目录下shift+右键打开cmd/powershell，执行auto_login~~

conf.ini ：
```
[user]
userid = 学号
password = 6位密码或8位密码

[run]
time_unit = 每次间隔的时间单位 （minutes/seconds） 
every_time = 每次间隔时间
begin_time = 允许登录时间
end_time = 不允许登录时间
log_level = 日志级别输出 （debug/info/warning）
```
exm：
```
[run]
time_unit = minutes
every_time = 10
begin_time = 07:00
end_time = 23:59
log_level = debug
# 早上7点到晚上23点59分内，每隔10分钟执行 判断是否需要登录校园网操作
```

>  
todo：   
登录失败返回页面报错信息      
周末的凌晨允许登录    
整合验证码识别的图片到程序中   
…
      
> v0.1.0 更新 
更新了windows ui     
修复了无数个bug     

> v0.0.3 更新     
修复了auto login 1获取重定向连接异常       

> v0.0.2 更新   
更新log输出   
修复无数个bug

