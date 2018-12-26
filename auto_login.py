import requests
import json
import os
import schedule
import sys
import logging

from time import sleep
from datetime import datetime
from base64 import b64encode
from configparser import ConfigParser

from ver_code import validation_code_recognition

test_url = 'http://quan.suning.com/getSysTime.do' # 测试连接状态url

conf = ConfigParser()
conf.read('conf.ini', encoding='utf-8')
if conf.get('run', 'log_level') == 'debug':
    log_level = logging.DEBUG
elif conf.get('run', 'log_level') == 'info':
    log_level = logging.INFO
elif conf.get('run', 'log_level') == 'warning':
    log_level = logging.WARNING
else:
    print('log level error.')
    sys.exit(1)

logging.basicConfig(
    # filename='run.log',
    format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=log_level,
    handlers=[logging.FileHandler("run.log"),logging.StreamHandler()]
)

def connect_wifi():
    logging.warning('正在连接到学校wifi')
    backinfo = os.system('netsh wlan connect name="ZQU-WebAuth"') # 连到学校wifi
    sleep(5)
    return backinfo
    
def check_wifi():
    """
    可以联网返回-1
    无网络连接返回0
    网络不可用返回1
    """
    try:
        test_status = requests.get(test_url)
        aa = json.loads(test_status.text)
        return -1 # 可以联网
    except requests.exceptions.ConnectionError: 
        # 未连接wifi
        return 0
    except json.decoder.JSONDecodeError:
        # 该wifi不能联网
        return 1
    return 2
    
def is_campus_network():
    """
    网络错误返回-1
    非局域网内返回0
    局域网内返回1
    """
    backinfo = os.popen('ping -w 1 10.0.1.51')
    result = backinfo.read()
    percent_sign = result.find('%')
    if percent_sign == -1:
        return -1
    elif result[percent_sign-3:percent_sign] == '100':
        return 0
    return 1

def online_time():
    now = datetime.now().strftime("%H:%M")
    if now > conf.get('run', 'begin_time') and now < conf.get('run', 'end_time'):
        return True
    return False

def auto_login_1(userId, password):
    logging.info('开始局域网验证')
    try:
        test_status = requests.get(test_url) # 获取重定向连接
    except requests.exceptions.ConnectionError:
        logging.error("重定向局域网失败")
    # logging.debug('局域网验证连接 {}'.format(test_status.url))
    if test_status.url.find('10.0.1.51') == -1: 
        logging.debug('已经通过局域网验证')
        return
    queryString = ''
    http_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
        'Cache-Control': 'no-cache', 
        'Connection': 'Keep-Alive',
        'Content-Length': '439',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': '10.0.1.51',
        'Origin': 'http://10.0.1.51',
        'Referer': '',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
    }
    try:
        http_headers['Referer'] = test_status.url
        queryString = test_status.url.split('?', 1)[1]
    except UnboundLocalError:
        logging.error('auto login 1 - UnboundLocalError')
    login_url = 'http://10.0.1.51/eportal/InterFace.do?method=login'
    rs = requests.post(
        url=login_url, 
        headers=http_headers, 
        data={
            'userId':userId, 
            'password':password, 
            'queryString':queryString
        }
    )
    return(rs.status_code)

def auto_login_2(userId, password):
    logging.info('开始电信验证')
    se = requests.session() # 新建会话
    test_status = se.get(test_url) # 获取重定向连接
    # logging.debug('局域网验证连接 {}'.format(test_status.url))
    if test_status.url.find('10.0.1.51') != -1: 
        logging.warning('未通过局域网验证')
        return
    login_2 = se.get(test_status.url)
    # 获取验证码图片
    v_code_image = open('test.jpg', 'wb+')
    code_url = 'http://enet.10000.gd.cn:10001/common/image.jsp'
    v_code_image.write(se.get(code_url, cookies=login_2.cookies).content)
    v_code_image.close()
    # 验证码识别
    v_code = validation_code_recognition('./test.jpg')
    logging.debug('验证码：{}'.format(v_code))
    post_text = {
       'edubas': '119.146.99.27',
       'eduuser': '10.72.99.58',
       'password1': str(b64encode(bytes(password, encoding="utf-8")), encoding="utf-8"),
       'patch': 'wifi',
       'rand': v_code,
       'userName1': userId,
    }
    http_headers = {
       'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8',
       'Accept-Encoding': 'gzip, deflate',
       'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
       'Cache-Control': 'max-age=0',
       'Connection': 'Keep-Alive',
       'Content-Length': '109',
       'Content-Type': 'application/x-www-form-urlencoded',
       'Host': 'enet.10000.gd.cn:10001',
       'Referer': '',
       'Upgrade-Insecure-Requests': '1',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
    }
    try:
        http_headers['Referer'] = test_status.url
    except UnboundLocalError:
        logging.error('auto login 2 - UnboundLocalError')
    
    login_http = 'http://enet.10000.gd.cn:10001/login.do'

    haha = se.post(url=login_http, headers=http_headers, data=post_text)
    
    return haha.status_code
    
def test():
    if not online_time():
        logging.info('不在验证时间段内')
        return -1
    if is_campus_network() != 1:
        connect_wifi()
    if check_wifi() == -1:
        logging.info('可以上网')
        return 0
    userid = conf.get('user', 'userid')
    password_long = conf.get('user', 'password')
    try:
        auto_login_1(userid, password_long[2:])
        auto_login_2(userid, password_long)
    except Exception as e:
        logging.error("未知异常：{}".format(e.message))

if __name__ == '__main__':
    logging.info('开始运行')
    logging.info('user is [{}]'.format(conf.get('user', 'userid')))
    logging.info('password is [{}]'.format(conf.get('user', 'password')))
    every_time = conf.getint('run', 'every_time')
    if conf.get('run', 'time_unit') == 'minutes':
        schedule.every(every_time).minutes.do(test)
    elif conf.get('run', 'time_unit') == 'seconds':
        schedule.every(every_time).seconds.do(test)
    else:
        logging.critical('conf文件错误')
        sys.exit(1)
    logging.info('每 {} {} 执行一次'.format(every_time, conf.get('run', 'time_unit')))
    logging.info('验证时间：{} 到 {}'.format(conf.get('run', 'begin_time'), conf.get('run', 'end_time')))
    while(1):
        schedule.run_pending()
        sleep(1)
        
        
        