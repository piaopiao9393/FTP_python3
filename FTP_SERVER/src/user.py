#! /usr/bin/env python
# -*- utf-8 -*-
__author__ = 'piaopiao9393'

import os,sys
import json,getpass
from FTP_CLIENT.lib.utils import md5,Config

class AdminUser(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'etc','config.ini')
        self.CONFIG = Config('E:\python_code\FTP\FTP_SERVER\etc\config.ini','SERVER')
        self.data = self.CONFIG.data_path
        self.user_db = os.path.join(self.CONFIG.db_path,'user.json')
        self.user_path = None
        self.dir_size = int(self.CONFIG.dir_size)*1024*1024
        if not os.path.exists(self.user_db):
            user_dict = {
                'admin':{
                    'password':md5('admin'),
                    'dir_size':self.dir_size,
                    'super_user':'1',
                    'lock_status':'0',
                    'user_dir':os.path.join(self.data,'admin')
                }
            }
            json.dumps(user_dict,open(self.user_db,'w'))
            user_home = os.path.join(self.data,'admin')
            os.mkdir(user_home)
    def registered(self,username,password):
        """
        注册用户
        :param username:用户名
        :param password: 密码
        :return: 返回成功/失败
        """
        user_dict = json.load(open(self.user_db,'r'))
        user_list = list(user_dict.keys())
        if username in user_list:
            print('用户已存在')
            return False
        user_dict[username] = {
            "password":password,
            "dir_size":self.dir_size,
            "super_user":'0',
            'lock_status':'0',
            'user_dir':os.path.join(self.user_db,username)
        }
        json.dump(user_dict,open(self.user_db,'w'))
        user_home = os.path.join(self.data,username)
        os.mkdir(user_home)
        return True

    def login(self,user_name,password):
        """
        y验证用户登录的相关操作
        :param user_name:
        :param password:
        :return:
        """
        with open(self.user_db,'r') as f:
            user_dict = json.load(f)

        user_list = list(user_dict.keys())
        if user_name not in user_list:
            return False
        if user_dict[user_name]["password"] == password:
            self.user_path = os.path.join(self.data,user_name)
            return True


