# coding:utf-8
'''
@author: ZainCheung
@LastEditors: ZainCheung
@description:网易云音乐全自动每日打卡300首歌升级账号等级,使用前请先到init.config文件配置
@Date: 2020-06-25 14:28:48
@LastEditTime: 2020-09-01 18:20:00
'''
from configparser import ConfigParser
from threading import Timer
import requests
import random
import hashlib
import datetime
import time
import json
import logging
import math
import os

'''
使用绝对路径时，切换到项目的当前目录。
'''
os.chdir(os.path.dirname(os.path.abspath(__file__)))
logFile = open("run.log", encoding="utf-8", mode="a")
logging.basicConfig(stream=logFile, format="%(asctime)s %(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)
grade = [10, 40, 70, 130, 200, 400, 1000, 3000, 8000, 20000]
api = ''


class Task(object):

    def __init__(self, uin, pwd, pushmethod, sckey, appToken, wxpusheruid, countrycode=86):
        self.uin = uin
        self.pwd = pwd
        self.countrycode = countrycode
        self.pushmethod = pushmethod
        self.sckey = sckey
        self.appToken = appToken
        self.wxpusheruid = wxpusheruid

    '''
    带上用户的cookie去发送数据
    url:完整的URL路径
    postJson:要以post方式发送的数据
    返回response
    '''

    def getResponse(self, url, postJson):
        response = requests.post(url, data=postJson, headers={'Content-Type': 'application/x-www-form-urlencoded'}, cookies=self.cookies)
        return response

    '''
    登录
    '''

    def login(self):
        data = {"uin": self.uin, "pwd": self.pwd, "countrycode": self.countrycode, "r": random.random()}
        if '@' in self.uin:
            url = api + '?do=email'
        else:
            url = api + '?do=login'
        response = requests.post(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        code = json.loads(response.text)['code']
        self.name = json.loads(response.text)['profile']['nickname']
        self.uid = json.loads(response.text)['account']['id']
        if code == 200:
            self.error = ''
        else:
            self.error = '登录失败，请检查账号'
        self.cookies = response.cookies.get_dict()
        self.log('登录成功')
        logging.info("登录成功")

    '''
    每日签到
    '''

    def play(self):
        url = api + '?do=listen&id=6968117636&time=500'
        response = self.getResponse(url, {"r": random.random()})
        data = json.loads(response.text)
        if data['code'] == 200:
            self.log('签到成功')
            logging.info('签到成功')
        else:
            self.log('重复签到')
            logging.info('重复签到')

    """
    开始执行
    """

    def start(self):
        try:
            self.list = []
            self.list.append("- 初始化完成\n\n")
            self.login()
            self.play()

        except:
            self.log('用户任务执行中断,请检查账号密码是否正确')
            logging.error('用户任务执行中断,请检查账号密码是否正确========================================')
        else:
            self.log('用户:' + self.name + '  今日任务已完成')
            logging.info('用户:' + self.name + '  今日任务已完成========================================')

    def log(self, text):
        time_stamp = datetime.datetime.now()
        print(time_stamp.strftime('%Y.%m.%d-%H:%M:%S') + '   ' + str(text))
        self.time = time_stamp.strftime('%H:%M:%S')
        self.list.append("- [" + self.time + "]    " + str(text) + "\n\n")


'''
初始化：读取配置,配置文件为init.config
返回字典类型的配置对象
'''


def init():
    global api  # 初始化时设置api
    config = ConfigParser()
    config.read('init.config', encoding='UTF-8-sig')
    uin = config['token']['account']
    pwd = config['token']['password']
    countrycode = config['token']['countrycode']
    api = config['setting']['api']
    md5Switch = config.getboolean('setting', 'md5Switch')
    peopleSwitch = config.getboolean('setting', 'peopleSwitch')
    pushmethod = config['setting']['pushmethod']
    sckey = config['setting']['sckey']
    appToken = config['setting']['appToken']
    wxpusheruid = config['setting']['wxpusheruid']
    print('配置文件读取完毕')
    logging.info('配置文件读取完毕')
    conf = {
        'uin': uin,
        'pwd': pwd,
        'countrycode': countrycode,
        'api': api,
        'md5Switch': md5Switch,
        'peopleSwitch': peopleSwitch,
        'pushmethod': pushmethod,
        'sckey': sckey,
        'appToken': appToken,
        'wxpusheruid': wxpusheruid
    }
    return conf


'''
MD5加密
str:待加密字符
返回加密后的字符
'''


def md5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()


'''
加载Json文件
jsonPath:json文件的名字,例如account.json
'''


def loadJson(jsonPath):
    with open(jsonPath, encoding='utf-8') as f:
        account = json.load(f)
    return account


'''
检查api
'''


def check():
    url = api + '?do=check'
    respones = requests.get(url)
    if respones.status_code == 200:
        print('api测试正常')
        logging.info('api测试正常')
    else:
        print('api测试异常')
        logging.error('api测试异常')


'''
任务池
'''


def taskPool():
    config = init()
    # 每天对api做一次检查
    check()
    print('账号: ' + config['uin'] + '  开始执行')
    logging.info('账号: ' + config['uin'] + '  开始执行========================================')
    if config['md5Switch'] is True:
        print('MD5开关已打开,即将开始为你加密,密码不会上传至服务器,请知悉')
        logging.info('MD5开关已打开,即将开始为你加密,密码不会上传至服务器,请知悉')
        config['pwd'] = md5(config['pwd'])
    task = Task(config['uin'], config['pwd'], config['pushmethod'], config['sckey'], config['appToken'], config['wxpusheruid'],
                config['countrycode'])
    task.start()


'''
程序的入口
'''
if __name__ == '__main__':
    taskPool()
