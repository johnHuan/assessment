# -*- coding: utf-8 -*-
# @Time    : 2024/8/15 12:23
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : app_socket.py

from flask_socketio import disconnect

from app import socketio, thread_lock
from commons.background import background_thread


def ack():
    # 似乎无用
    print('message was received!')


# 关闭时
@socketio.on('disconnect_request', namespace='/conn_logging')
def disconnect_request():
    print('Client disconnected')
    disconnect()


# 连接时
@socketio.on('connect', namespace='/conn_logging')
def connect():
    global thread
    socketio.emit('message',
                  {'data': "已经成功创建连接!"}, namespace='/conn_logging', callback=ack)
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
