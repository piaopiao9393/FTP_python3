#! /usr/bin/env python
# -*- utf-8 -*-
__author__ = 'piaopiao9393'
import sys
import time
import hashlib
import configparser
import os,json
def md5(arg):
    """
    md5加密
    :param arg:
    :return:
    """
    obj = hashlib.md5(bytes('zaibiekangqiao',encoding = 'utf-8'))
    obj.update(bytes(arg,encoding = 'utf-8'))
    return obj.hexdigest()

class Config(object):
    """
    读取配置文件
    """
    def __init__(self,config_path,section='DEFAULTS'):
        self.section = section
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.read(config_path,encoding='utf-8')
    def __getattr__(self, item):
        return self.config.get(self.section, item)

config = Config('E:\python_code\FTP\FTP_SERVER\etc\config.ini','SERVER')
with open(r'E:\python_code\FTP\FTP_SERVER\db\user.json','r') as f:
    text = json.load(f)


