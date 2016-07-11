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

import logging
logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)

HOST = DefaultConfig.LORA_HOST
APP_EUI = DefaultConfig.LORA_APP_EUI
TOKEN = DefaultConfig.LORA_TOKEN
PORT = DefaultConfig.LORA_PORT

# socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})

def ws_listening():
    userver_thread = Thread(target=userver_listening)
    # userver_thread.setDaemon(True)
    userver_thread.start()


def userver_listening():
    try:
        socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})
        # global socketio_cli
        test_namespace = socketio_cli.define(TestNamespace, '/test')
        socketio_cli.wait()

    except Exception as e:
        ws_listening()


class Switchor(object):
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
    def __init__(self, euis, namespace, data='00'):
        self.euis = euis
        self.namespace = namespace
        self.data = data

    def turn_on_off_by_group(self):
        # todo: 发送动态组播信息
        self.namespace.emit('tx', self._get_group_sending_data())

    def turn_on_off_one_by_one(self):
        for eui in self.euis:
            print('emit ', self._get_sending_data(eui))
            self.namespace.emit('tx', self._get_sending_data(eui))

    def _get_group_sending_data(self):
        # todo: 生成动态组播数据
        pass

    def _get_sending_data(self, eui):
        return {
            'cmd': 'tx',
            'EUI': eui,
            'port': 1,
            'rx_window': 1,
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
            self.cook_rx_message(msg)
            # todo: 处理失败提示

        def on_enqueued(self):
            print('enqueued')
            print(self)

        def on_connect_error(self, msg):
            print('connect error')
            print(msg)

        def cook_rx_message(self, message):
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

                # 更改开关状态
                alter_switch_status(cx, message.get('EUI'))

                # 对数据分析，收到开关的信息时，判断当前的状态，如果对应电灯的on_count是0，on_count++， 如果on_count 为1
                lights_eui = []
                for info in get_lights_info(cx, message.get('EUI')):

                    if not get_light_on_count(cx, info[0]):           # 如果是0，电灯状态改变（发送一个信号，转到反转当前状态）
                        lights_eui.append(info[0])

                # TODO 发送数据
                # global socketio_cli
                swicthor = Switchor(lights_eui, self)
                swicthor.turn_on_off_one_by_one()

                print('发送成功')
                # TODO:更新灯的数据
                # print('发送组播', swicthor._get_sending_data())


def get_euis(cx):
    exe = 'SELECT eui FROM switchs'
    return cx.execute(exe).fetchall()


def get_group_eui(cx, eui):
    exe = 'SELECT group_eui from switchs where eui="{}"'.format(eui.upper())
    try:
        return cx.execute(exe).fetchone()[0]
    except TypeError:
        return None


def alter_switch_status(cx, switch_eui):
    """
    转换状态
    :param cx:
    :param switch_eui:
    :return:  if on = 0 : on = 1 else : on = 0
    """
    exe = 'UPDATE switchs ' \
          'SET "on" = CASE ' \
                    'WHEN "on" = 0 THEN 1 ' \
                    'ELSE 0 ' \
                    'END ' \
          'WHERE eui = "{}"'.format(switch_eui)

    cx.execute(exe)
    cx.commit()

def get_lights_info(cx, switch_eui):
    """
    获取开关对应的电灯信息
    :param cx:
    :param switch_eui:
    :return: [(eui， on_count), (eui, on_count),...]
    """
    exe = 'SELECT eui, on_count FROM lights WHERE id IN ' \
          '(SELECT light_id FROM ltsw_association WHERE switch_id = (SELECT id FROM switchs WHERE eui="{}"))'.format(switch_eui)
    return cx.execute(exe).fetchall()


def get_light_on_count(cx, light_eui):
    """
    获取电灯关联开关的数目
    :param cx:
    :param light_eui:
    :return:
    """
    exe = 'SELECT SUM("on") FROM switchs WHERE id IN ' \
          '(SELECT switch_id FROM ltsw_association WHERE light_id = (SELECT id FROM lights WHERE eui="{}"))'.format(light_eui)
    return cx.execute(exe).fetchone()[0]


def on_act_tx(msg):
    print('on_act_tx')
    print(msg)

if __name__ == '__main__':
    import time
    # class MSocketIO(SocketIO):
    #     def define(self, Namespace, path=''):
    #         self._namespace_by_path[path] = namespace = Namespace(self, path)
    #         if path:
    #             self.connect(path)
    #         return namespace
    #
    # socketio_cli = MSocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})
    # test_namespace = TestNamespace(socketio_cli, '/test')
    #
    # test_namespace.on('act_tx', on_act_tx)
    # test_namespace.on('connect', on_act_tx)
    # test_namespace.emit('tx', {'cmd': 'tx',
    #         'EUI': '3530353460358D0B',
    #         'port': 1,
    #         'rx_window': 1,
    #         'data': '0033ffff'})
    # print('emit')
    # socketio_cli.wait(100)
    cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)
    print(get_group_eui(cx, 'DEFIEDFFEASSF'))
    print(get_lights_info(cx, '3530353460358D0B'))
    print(get_light_on_count(cx, '3530353460358D0B'))
    print(alter_switch_status(cx, '3530353460358D0B'))
