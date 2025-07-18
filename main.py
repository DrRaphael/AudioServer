# -*- coding: utf-8 -*-

import socket
import time
import threading
import json
from log import logger
from config import config


class Server:
    def __init__(self):
        # 建立两个TCP服务端
        self.control_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []

    def start(self):
        self.control_server.bind((config['network']['interface'], config['network']['port']['control']))
        self.audio_server.bind((config['network']['interface'], config['network']['port']['audio']))
        self.control_server.listen(config['server']['maxClient'])
        self.audio_server.listen(config['server']['maxClient'])

    def control(self):
        while True:
            control_client, control_address = self.control_server.accept()
            thread = threading.Thread(target=self.control_handle, args=(control_client, control_address))
            thread.daemon = True
            thread.start()

    def control_handle(self, connect, address):
        logger.info(f"Client {address} is connected")
        auth_flag = 3
        while True:
            data = connect.recv(1024)
            if self.auth(data):
                connect.send(b'Authentication Successful\n')
                break
            else:
                auth_flag -=1
                connect.send(b'Authentication Failed\n')
                logger.warning(f"Client {address} authentication failed! Your can Try {auth_flag}")
            if auth_flag == 0:
                # 断开连接
                connect.send(b'Connection Refused By Server')
                connect.close()
                return False
        while True:
            try:
                data = connect.recv(1024)
                self.prase_cmd(data)
                connect.send(b'OK')
                if not data:
                    logger.info(f"Client {address} disconnected!")
                    break
                logger.info(f"Recv {data}")
            except e:
                logger.warning(f"Error {e}")


    def auth(self,data):
        if not self.isJson(data):
            return False
        return json.loads(data)['authentication'] == config['server']['authentication']

    def isJson(self, data):
        try:
            json.loads(data)
            return True
        except:
            return False

    def prase_cmd(self, data):
        pass



# 判断数据是否是json数据


if __name__ == '__main__':
    server = Server()
    server.start()
    server.control()
