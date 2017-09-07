#! /usr/bin/env python
# -*- utf-8 -*-
import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from FTP_CLIENT.src.socket_client import Client

if __name__ == '__main__':
    host,port = ('127.0.0.1',8888)
    obj = Client(host,port)
    obj.main()