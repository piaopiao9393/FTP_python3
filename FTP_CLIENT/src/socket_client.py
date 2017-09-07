#! /usr/bin/env python
# -*- utf-8 -*-
__author__= 'piaopiao9393'
import os
import sys
import json
import socket
import getpass
from FTP_CLIENT.lib.utils import md5


class Client(object):
    def __init__(self,ip,port):
        self.host = ip
        self.port = port
        self.user_name = None
        self.socket = socket.socket()

    def main(self):
        """
        使用反射方式调用各种方法
        :return:
        """
        if self.login():
            while True:
                command = input('ftp->>')
                if len(command)==0:
                    continue
                elif command == 'exit':
                    exit()
                cmd = command.split()[0]
                if hasattr(self,cmd):
                    func = getattr(self,cmd)
                    func(command)
                else:
                    print('非法指令，请输入合法的操作!')

    def login(self):
        print("连接至",self.host)
        user_name = input("账号名:")
        #password = getpass.getpass("密码:")
        password = input("密码：")
        login_dict = {
            'command':'login',
            'user_name': user_name,
            'password': md5(password)
        }
        self.user_name = user_name
        login_info = json.dumps(login_dict)
        self.socket.connect((self.host,self.port))
        self.socket.sendall(bytes(login_info,encoding='utf-8'))
        login_status = str(self.socket.recv(1024),encoding='utf-8')
        print(login_status)
        if login_status == '登录成功':
            return True
        else:
            return False
    def help(self,command_str=None):
        help_menu='''
            [帮助信息]
            put             上传文件
            get             下载文件
            ls              查看文件
            pwd             当前目录
            cd              切换当前目录
            du              查看文件大小
            mkdir           创建目录
            remove          删除
            help            查看帮助文档
        '''
        print(help_menu)
    def put(self,command_str):
        """
        向服务器上传文件
        :param command_str: put   上传文件名
        :return:
        """
        command_list = command_str.split()
        file = command_list[1]
        file_size = os.stat(file).st_size
        file_md5 = md5(str(file_size))
        file_name = os.path.basename(file)
        #将命令汇总成字典，方便传输
        command_dict = {
            "command":"put",
            "file_name":file_name,
            "file_size":file_size,
            "file_md5":file_md5,
        }
        #路径是可选参数
        if len(command_list)==3:
            file_path = command_list[2]
            command_dict["file_path"] = file_path
        command_msg = json.dumps(command_dict)
        self.socket.sendall(bytes(command_msg,encoding='utf-8'))
        feedback = str(self.socket.recv(1024),encoding='utf-8')
        if feedback == '开始传输文件!':
            print(feedback+'1\n')
            try:
                with open(file,'rb') as f:
                    send_size = 0
                    for line in f:
                        self.socket.sendall(line)
                        send_size += len(line)
                        #进度格显示，稍后做
                        #self.ProgressBat.update(send_size,file_size)
            except:
                print("传输中断！")
        elif feedback=='继续传输文件':
            print(feedback+'2\n')
            continue_length = int(str(self.socket.recv(1024),encoding='utf-8'))
            try:
                with open(file,'rb') as f:
                    f.seek(continue_length)
                    send_size = continue_length
                    for line in f:
                        self.socket.sendall(line)
                        send_size += len(line)
                        # 进度格显示，稍后做
                        # self.ProgressBat.update(send_size,file)
            except:
                print('传输中断')
        else:
            print(feedback)
            return
        #接收put操作的结果
        result = str(self.socket.recv(1024),encoding='utf-8')
        print(result+'3')

    def get(self,command_str):
        """
        下载文件
        :param command_str:
        :return:
        """
        command_list = command_str.split()
        file_name = command_list[1]
        des_path = os.path.abspath(os.path.curdir)
        if len(command_list)==3:
            des_path = command_list[2]
            if not os.path.isdir(des_path):
                print('%s不是合法路径'%des_path)
                return False
        command_dict ={
            "command":"get",
            "file_name":file_name,
        }
        command_msg = json.dumps(command_dict)
        self.socket.sendall(bytes(command_msg,encoding='utf-8'))
        file_status = str(self.socket.recv(1024),encoding='utf-8')
        if file_status.startswith('Error'):
            print(file_status)
            return False
        file_status = json.loads(file_status)
        file_name = file_status['file_name']
        file_size = file_status['file_size']
        file_md5 = file_status['file_md5']
        file_path = os.path.join(des_path,file_name)
        if os.path.exists(file_path):
            if md5(os.stat(file_path).st_size)==file_md5:
                print("目标文件已存在")
                return False
            print("续传文件:")
            self.socket.sendall(bytes('续传文件',encoding='utf-8'))
            recv_size = os.stat(file_path).st_size
            continue_length = str(recv_size)
            self.socket.sendall(bytes(continue_length,encoding='utf-8'))
            try:
                with open(file_path,'ab') as file:
                    while recv_size < file_size:
                        recv_data = self.socket.recv(1024)
                        file.write(recv_data)
                        recv_size += len(recv_data)
                        #更新进度条
                return True
            except Exception as error:
                print('获取文件途中出错:%s'%error)
        else:
            self.socket.sendall(bytes("从头获取文件",encoding='utf-8'))
            recv_size = 0
            try:
                with open(file_path,'wb') as file:
                    while recv_size < file_size:
                        recv_data = self.socket.recv(1024)
                        file.write(recv_data)
                        recv_size += len(recv_data)
                        #更新进度条
                return True
            except Exception as error:
                print('获取文件途中出错:%s'%error)
        if md5(str(os.stat(file_path).st_size))==file_md5:
            print('文件传输完成')
            return True





