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


def ws_listening():
    userver_thread = Thread(target=userver_listening)
    # userver_thread.setDaemon(True)
    userver_thread.start()


def userver_listening():
    try:
        socketio_cli = SocketIO(host=HOST, port=PORT, params={'app_eui': APP_EUI, 'token': TOKEN})
        test_namespace = socketio_cli.define(TestNamespace, '/test')
        socketio_cli.wait()

    except Exception as e:
        ws_listening()

def _on_message(ws, message):
    print(message)
    cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)
    t = json.loads(message)
    # if t['h'] and t['data'][0:8] == '0027a208':
    if not hasattr(t, 'h'):
        data = t['data']
        if len(data) >= 24:
            insert_data(cx, data)


def _on_open(ws):
    print(u'connect loriot webserver successfully')


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
        data = message['data']
        if len(data) >= 24:
            insert_data(cx, data)


def get_info(cx, mac):
    exe = "select id, garbage_can_id from device where mac='%s'" % mac
    dev_info = cx.execute(exe).fetchall()
    if dev_info:
        info = []
        for res in dev_info:
            if res[1]:
                bt_exe = "select bottom_height, top_height from garbage_can where id=%s" % res[1]
                bottom_top_height = cx.execute(bt_exe).fetchone()
                if bottom_top_height:
                    t = (res[0], bottom_top_height[0], bottom_top_height[1])
                    info.append(t)
                else:
                    info.append((res[0], None, None))
        return info


def insert_data(cx, data):
    mac = data[0:8].upper()
    infos = get_info(cx, mac)
    now = datetime.now()

    for res in infos:
        if res:
            device_id = res[0]
            bottom_height = res[1]
            top_height = res[2]
            if device_id:
                if bottom_height and bottom_height > top_height:
                    info = parse_data(data, bottom_height, top_height)
                    ins_data = (None, device_id, data, info[0], info[1], info[2], now)
                else:
                    ins_data = (None, device_id, data, 0, 0, 0, now)

                cx.execute('insert into data values (?,?,?,?,?,?,?)', ins_data)
                cx.commit()

    # emit new message to web
    socketio.emit(mac, {'occupancy': ins_data[3], 'temperature': ins_data[4],
                        'electric_level': ins_data[5], 'create_time': now.strftime('%y/%m/%d %H:%M:%S')},
                  namespace='/device')


def parse_data(raw_data, bottom_height, top_height):
    """
    解析出数据
    :param raw_data: 原始数据
    :param height: 探头到垃圾桶底部距离
    :return:  (占用率， 温度， 剩余电量等级)
    数据解析如下：
    例如：a8c63b90bb00180713000371为服务器收到的16进制数据，解析如下：
        第0~3字节：a8c63b90为终端的32位设备地址
        第4字节：bb为超声波探头到被测平面的测量值，单位cm.转化十进制为187cm
        第5字节：00为第二路超声波测量值，默认没有第二路超声波，为0。意义同上。
        第6字节：18为终端测量的16进制温度值。转化为十进制为24℃。
        第7字节：07为终端电池剩余电量等级，一共7个等级。
                  07表示剩余电量为95%~100%，06为85%，06为70%，04为50%，04为50%，03为35%，02为25%，01为10%，00为0%
        第8~10字节：13 00 03为本终端的时间值，以BCD码形式表示，采24小时制，分别为时、分和秒，当终端收到服务器的同步时间后，此值为实际实时时间。
        第11字节：71为前面11个字节有异或校验值
    """
    assert bottom_height > top_height, u'底部高度应该大于顶部高度'
    current_height = int(raw_data[8:10], 16)
    # 占用率， 0 - 100， 以5为最小单位
    t = ((bottom_height - current_height) / (bottom_height - top_height)) * 100
    dm = divmod(t, 5)
    occupancy = dm[0] * 5
    if occupancy < 0:
        occupancy = 0
    if occupancy > 100:
        occupancy = 100

    temperature = int(raw_data[12:14], 16)
    electric_level = int(raw_data[14:16], 16)
    if electric_level >= 7:
        electric_level = 100
    elif electric_level < 0:
        electric_level = 0
    else:
        electric_level = electric_level * 15

    return (occupancy, temperature, electric_level)


if __name__ == '__main__':
    # cx = sqlite3.connect(DefaultConfig.DATABASE_PATH)
    # cx.execute('insert into data values (?,?,?,?,?,?,?)', (None, 20, 'sdfa', 12, 12,2, 'hello'))
    # cx.commit()
    pass