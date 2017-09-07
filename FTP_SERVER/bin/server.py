#! /usr/bin/env python
# -*- utf-8 -*-
__author__ = 'piaopiao9393'
import os,sys,socketserver
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from FTP_CLIENT.lib.utils import Config
from FTP_SERVER.src.socket_server import MyServer



config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'etc','config.ini')

CONFIG = Config(config_path,'SERVER')

if __name__ == '__main__':
    run = socketserver.ThreadingTCPServer((CONFIG.listen,int(CONFIG.port)),MyServer)
    run.serve_forever()


