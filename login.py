import requests
import json
import os
from time import sleep
from datetime import datetime
from base64 import b64encode
from urllib import parse
from ver_code import validation_code_recognition
from urllib.parse import parse_qs, urlparse

from config import logger, conf

test_url = 'http://quan.suning.com/getSysTime.do'  # 测试连接状态url

def connect_wifi():
    logger.warning('正在连接到学校wifi')
    backinfo = os.system('netsh wlan connect name="ZQU-WebAuth"')  # 连到学校wifi
    sleep(5)
    return backinfo

def check_net():
    """
    可以联网返回-1
    无网络连接返回0
    网络不可用返回1
    """
    try:
        test_status = requests.get(test_url)
        aa = json.loads(test_status.text)
        return -1  # 可以联网
    except requests.exceptions.ConnectionError:
        # 未连接wifi
        return 0
    except json.decoder.JSONDecodeError:
        # 该wifi不能联网
        return 1
    return 2


def is_campus_network():
    """
    判断是否校园网

    网络错误返回-1
    非局域网内返回0
    局域网内返回1
    """
    # backinfo = os.popen('ping -w 1 10.0.1.51')
    # result = backinfo.read()
    # percent_sign = backinfo.find('%')
    # if percent_sign == -1:
    #     return -1
    # elif result[percent_sign - 3:percent_sign] == '100':
    #     return 0
    # return 1
    try:
        requests.get('http://10.0.1.51')
    except:
        logger.debug("不在校园网")
        return 0
    else:
        logger.debug("在校园网")
        return 1

def online_time():
    now = datetime.now().strftime("%H:%M")
    print(conf.get('run', 'end_time'))
    if now > conf.get('run', 'begin_time') and now < conf.get('run', 'end_time'):#旧版本
        return True
    return False


def auto_login_1(userid, password):
    logger.info('开始局域网验证')
    logger.info('学号：' + userid + ' 密码:' + password)

    try:
        test_status = requests.get(test_url)  # 获取重定向连接
    except requests.exceptions.ConnectionError:
        logger.error("重定向局域网失败")
        return
    if test_status.url.find('10.0.1.51') == -1:
        logger.debug('已经通过局域网验证')
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
        logger.error('auto login 1 - UnboundLocalError')
        pass
    login_url = 'http://10.0.1.51/eportal/InterFace.do?method=login'
    rs = requests.post(
        url=login_url,
        headers=http_headers,
        data={
            'userId': userid,
            'password': password,
            'queryString': queryString
        })
    return rs.status_code


def auto_login_2(userid, password):
    logger.info('开始电信验证')
    logger.info('学号：'+userid+' 密码:'+password)

    se = requests.session()  # 新建会话
    test_status = se.get(test_url)  # 获取重定向连接
    if test_status.url == test_url:
        logger.info('可以上网')
        return
    if test_status.url.find('10.0.1.51') != -1:
        logger.warning('未通过局域网验证')
        return
    login_2 = se.get(test_status.url)

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

    url_parse_dict = dict()

    try:
        http_headers['Referer'] = test_status.url
        url_parse = parse.urlparse(test_status.url) # 获取链接参数
        url_parse_dict = parse.parse_qs(url_parse.query)
    except UnboundLocalError:
        logger.error('auto login 2 - UnboundLocalError')
    except KeyError:
        logger.error('auto login 2 - KeyError 重定向链接{}'.format(test_status.url))

    # 获取验证码图片
    v_code_image = open('test.jpg', 'wb+')
    code_url = 'http://enet.10000.gd.cn:10001/common/image.jsp'
    # print(se.get(code_url, cookies=login_2.cookies).content)
    v_code_image.write(se.get(code_url, cookies=login_2.cookies).content)
    v_code_image.close()
    # 验证码识别
    v_code = validation_code_recognition('./test.jpg')
    os.remove('./test.jpg')#删除验证码文件
    logger.debug('验证码：{}'.format(v_code))


    sleep(2)

    post_text = {
        'edubas': url_parse_dict['wlanacip'],
        'eduuser': url_parse_dict['wlanuserip'],
        'password1': str(b64encode(bytes(password, encoding="utf-8")), encoding="utf-8"),
        'patch': 'wifi',
        'rand': v_code,
        'userName1': userid,
    }

    login_http = 'http://enet.10000.gd.cn:10001/login.do'

    haha = se.post(url=login_http, headers=http_headers, data=post_text)

    return haha.status_code


def main(userid, password):
    logger.info('验证时间段')
    if not online_time():
        logger.info('不在验证时间段内')
        return -1
    logger.info('判断校园网')
    if is_campus_network() != 1:
        connect_wifi()
        # return 0

    logger.info('判断联网状态')
    if check_net() == -1:
        logger.info('可以上网')
        return 0
    try:
        # 若密码长度为6当成移动网络，8位电信网络
        if len(password) == 6:
            auto_login_1(userid, password)
        elif len(password) == 8:
            auto_login_1(userid, password[2:])
            sleep(2)
            auto_login_2(userid, password)
        else:
            logger.error("密码错误")

    except Exception as e:
        logger.error("未知异常：{}".format(e))


def logout_campus_network():
    logger.info('登出')
    se = requests.session()
    try:
        test_status = se.get('http://10.0.1.51')  # 获取重定向连接
        user_index = parse_qs(urlparse(test_status.url).query)['userIndex'][0]
    except requests.exceptions.ConnectionError:
        logger.warning("未连接校园网")
        return
    except KeyError:
        logger.error('key error: 获取user index失败，请检查是否登录成功')
        return
    except Exception as e:
        logger.error('ERROR: {}'.format(e))
        return
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
    logout_url = 'http://10.0.1.51/eportal/InterFace.do?method=logout'
    res = se.post(
        logout_url, data={'userIndex': user_index}, headers=http_headers)
    logger.info('登出状态：{}'.format(res.status_code))
    return res.status_code

