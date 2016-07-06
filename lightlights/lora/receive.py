# -*- coding: utf-8 -*-
from __future__ import division
import websocket
from lightlights.config import DefaultConfig
import sqlite3
import json
from datetime import datetime
from lightlights.extentions import socketio
from flask_socketio import emit
from flask import current_app
from socketIO_client import SocketIO, BaseNamespace
from threading import Thread

HOST = DefaultConfig.LORA_HOST
APP_EUI = DefaultConfig.LORA_APP_EUI
TOKEN = DefaultConfig.LORA_TOKEN
PORT = DefaultConfig.LORA_PORT

socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})

def ws_listening():
    userver_thread = Thread(target=userver_listening)
    # userver_thread.setDaemon(True)
    userver_thread.start()


def userver_listening():
    try:
        # socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})
        global socketio_cli
        test_namespace = socketio_cli.define(TestNamespace, '/test')
        socketio_cli.wait()

    except Exception as e:
        ws_listening()


class Switchor():
    """
    开关灯
     Event: 'tx' (Sending plain Multicast Message to a multicast group of devices)
        Direction: Client to Server
        Data Format:
        {
            cmd      : 'mtx';	// must always have the value 'tx'
            EUI      : string;  // Multicast Group EUI, 8 hex digits (without dashes)
            port     : number;  // port to be used (1..223)
            data     : string;  // data payload (to be encrypted by our server)
                                // if no APPSKEY is assigned to device, this will return an error
                                // string format based on application setup (default is hex string)
        }

        """
    def __init__(self, group_eui, socketio_cli,data=''):
        self.group_eui = group_eui
        self.socketio_cli = socketio_cli
        self.data = data

    def turn_on_off(self):

        self.socketio_cli.emit('tx', self._get_sending_data())

    def _get_sending_data(self):
        return {
            'cmd': 'mtx',
            'EUI': self.group_eui,
            'PORT': 1,
            'data': self.data
        }


class TestNamespace(BaseNamespace):
        def on_connect(self):
            print('socket io connected')

        def on_disconnect(self):
            print('socket io disconnected')

        def on_error_msg(self):
            print('error occured')
            print(self)

        def on_post_rx(self, msg):
            print('get post msg')
            cook_rx_message(msg)
            # todo: 处理失败提示

        def on_enqueued(self):
            print('enqueued')
            print(self)

        def on_connect_error(self, msg):
            print('connect error')
            print(msg)


def cook_rx_message(message):
    """
    处理接收到的信息
    :param message:
    :return:
    """
    print(message)
    cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)
    if not isinstance(message, dict):
        message = json.loads(message)
    # if t['h'] and t['data'][0:8] == '0027a208':
    if not hasattr(message, 'h'):
        eui = message.get('EUI')
        group_eui = get_group_eui(cx, message.get('EUI'))
        if group_eui:
            # TODO 发送数据
            global socketio_cli
            swicthor = Switchor(group_eui, socketio_cli)
            swicthor.turn_on_off()
            # TODO:更新灯的数据

            print('发送组播', swicthor._get_sending_data())


def get_euis(cx):
    exe = 'SELECT eui FROM switchs'
    return cx.execute(exe).fetchall()


def get_group_eui(cx, eui):
    exe = 'SELECT group_eui from switchs where eui={}'.format(eui.upper())
    return cx.execute(exe).fetchone()

if __name__ == '__main__':
    cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)
    print(get_group_eui(cx, '2233445566778880')[0])