#! /usr/bin/env python
# -*- utf-8 -*-
__author__ = 'piaopiao9393'
import os,sys,re,json,getpass,socketserver
from FTP_CLIENT.lib.utils import md5,Config
from FTP_SERVER.src.user import AdminUser

#读取配置文件信息
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'etc','config.ini')
#config_path = 'E:/python_code/FTP/FTP_SERVER/etc/config.ini'
#print(config_path)
CONFIG = Config(config_path,'SERVER')
#调用用户管理的类
admin_user = AdminUser()

class MyServer(socketserver.BaseRequestHandler,AdminUser):
    user_json = json.load(open(os.path.join(CONFIG.db_path,'user.json'),'r'))

    user_name = None
    user_path = None
    current_path = None
    def handle(self):
        while True:
            try:
                command_str = str(self.request.recv(1024),encoding='utf-8')
                if len(command_str) == 0:
                    print('命令不能为空，请重输：')
                    break
                else:
                    self.cmd(command_str)

            except Exception as error:
                print("Error:%s"%error)
                break
    def cmd(self,command_str):
        """
        使用反射调用各种操作
        :param str:传过来的是一个json格式的数据，直接取键值为‘command’的值即可
        :return:
        """
        command_dict = json.loads(command_str)
        command = command_dict['command']
        #通过反射调用各操作
        if hasattr(self,command):
            func = getattr(self,command)
            func(command_dict)
            return True
    def _new_path(self,path):
        """
        真实路径转换成客户端可以看到的路径
        :param path:
        :return:
        """
        #真实路径转客户看到的路径
        if path.startswith(self.user_path):
            path = re.sub(self.user_path,'',path)
            return path
        #客户端的路径转换为真实的路径
        if path.startswith('/'):
            path = os.path.join(self.user_path,re.sub('/','',path,1))
            return path
        path = os.path.join(self.current_path,path)
        return path
    def _get_size(self,file_path):
        """
        计算文件或目录的大小
        :param file_path:
        :return:
        """
        if not os.path.exists(file_path):
            return 0
        if os.path.isfile(file_path):
            return os.path.getsize(file_path)
        size = 0
        for root,dirs,files in os.walk(file_path):
            size += sum([os.path.getsize(os.path.join(root,name)) for name in files])
        return size




    def login(self,command_dict):
        """
        用户登录的相关操作
        :param command_dict:
        :return:
        """
        user_name = command_dict["user_name"]
        password = command_dict["password"]
        if admin_user.login(user_name,password):
            self.user_name = user_name
            self.user_path = os.path.join(CONFIG.data_path,user_name)
            self.current_path = self.user_path
            self.request.sendall(bytes('登录成功',encoding='utf-8'))
        else:
            self.request.sendall(bytes('登录失败',encoding='utf-8'))


    def put(self,command_dict):
        """
        上传文件服务器端操作
        :param command_dict:
        :return:
        """
     #   print(command_dict)
        file_name = command_dict['file_name']
        file_size = command_dict['file_size']
        file_md5 = command_dict['file_md5']
        user_size = self.user_json[self.user_name]['dir_size']
        user_du = self._get_size(self.user_path)
        user_size -= user_du
        #判断文件大小是否满足用户空间的限制
        if file_size > user_size:
            self.request.sendall(bytes("文件大小超过用户空间限制",encoding='utf-8'))
            return False
        #判断用户是否传入文件路径
        if command_dict.get('file_path'):
            path = command_dict['file_path']
            file_path = os.path.join(self._new_path(path),file_name)
        else:
            file_path = os.path.join(self.current_path,file_name)
        #判断文件是否存在，存在的话检测是否上传完毕，未完毕的话断点续传
        if os.path.exists(file_path):

            des_md5 = md5(str(os.stat(file_path).st_size))
            if des_md5 == file_md5:
                self.request.sendall(bytes("文件已存在",encoding='utf-8'))
                return False
            #文件存在，但不完整，断点续传
            self.request.sendall(bytes('继续传输文件',encoding='utf-8'))
            continue_length = os.stat(file_path).st_size
            send_length = str(os.stat(file_path).st_size)
            self.request.sendall(bytes(send_length,encoding='utf-8'))
        #接受bytes字节数据，追加写
            try:
                with open(file_path,'ab') as file:
                    while continue_length<file_size:
                        recv_data = self.request.recv(1024)
                        file.write(recv_data)
                        continue_length += len(recv_data)
            except:
                print("文件传输中断")
        #文件不存在，从头开始传输
        else:
            print("开始传输文件")
            self.request.sendall(bytes('开始传输文件!',encoding='utf-8'))
            recv_size = 0
            try:
                with open(file_path,'wb') as file:
                    while recv_size<file_size:
                        recv_data = self.request.recv(1024)
                        file.write(recv_data)
                        recv_size += len(recv_data)
            except:
                print("文件传输中断")
        #最后校验文件
        des_md5 = md5(str(os.stat(file_path).st_size))
        if des_md5 == file_md5:
            self.request.sendall(bytes("文件传输完毕",encoding='utf-8'))
        else:
            self.request.sendall(bytes("传输过程中出现问题",encoding='utf-8'))

    def get(self,command_dict):
        """
        下载文件
        :param command_dict:
        :return:
        """
        file_name = command_dict['file_name']
        file_path = self._new_path(file_name)
        if not os.path.exists(file_path):
            self.request.sendall(bytes('文件不存在',encoding='utf-8'))
            return False
        file_size = os.stat(file_path).st_size
        file_md5 = md5(str(file_size))
        file_name = os.path.basename(file_path)
        file_status = {
            'file_name':file_name,
            'file_size':file_size,
            'file_md5':file_md5,
        }

        file_status = json.dumps(file_status)
        self.request.sendall(bytes(file_status,encoding='utf-8'))
        recv_status = str(self.request.recv(1024),encoding='utf-8')
        if recv_status == '从头获取文件':
            try:
                with open(file_path,'rb') as file:
                    for line in file:
                        self.request.sendall(line)
            except:
                print('传输文件中断')
        elif recv_status == '续传文件':
            continue_length = int(str(self.request.recv(1024),encoding='utf-8'))
            try:
                with open(file_path,'rb') as file:
                    file.seek(continue_length)
                    for line in file:
                        self.request.sendall(line)
            except:
                print('文件传输中断')



