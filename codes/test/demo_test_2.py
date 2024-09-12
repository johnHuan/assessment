# -*- coding: utf-8 -*-
# @Time    : 2024/9/1 22:10
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : demo_test_2.py

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,  cors_allowed_origins="*")

if __name__ == '__main__':
    socketio.run(app)
