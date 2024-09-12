# -*- coding: utf-8 -*-
# @Time    : 2024/9/10 10:43
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : demo_test_3.py
# -*- coding:utf-8 -*-

from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Lock
import random

from codes.generate_log import read_logs

async_mode = None
app = Flask(__name__, static_folder='/', template_folder="/")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许跨域
thread = None
thread_lock = Lock()


# 如果访问地址中包含 /、/index、/index.html,则映射到index.html界面
@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    print('index')
    return render_template('index.html')


# 连接上socket后，需要做的事情 connect为连接的事件，固定这么写
@socketio.on('connect', namespace='/msg')
def test_connect():
    print('连接上socket服务')
    global thread
    with thread_lock:
        if thread is None:
            print(thread)
            thread = socketio.start_background_task(target=background_thread)
            print('thread is none create')


def callback_a():
    print('service callback success')


def callback_b():
    print('html callback success')


def background_thread():
    while True:
        socketio.sleep(10)
        t = random.randint(1, 100)
        msg = {'data': t}
        print(msg)
        socketio.emit('a', msg, namespace='/msg', callback=callback_a())
        print(t)


# 接收到消息做的事情 message为接收消息的事件，如果是接收到的文本，用message，接收json，用json，固定这么写
@socketio.on('message', namespace='/msg')
def text(message):
    print(message)
    room = 'room1'
    t = random.randint(1, 100)
    msg = 'service-message-' + str(t)
    print(msg)
    socketio.emit('a', {'msg': msg}, namespace='/msg', callback=callback_b())


def my_log_():
    # filename = os.path.join(configs['log_path'], 'log.log')
    # while True:
    #     p = subprocess.Popen(['tail', '-n', '10', filename], shell=True, stdout=subprocess.PIPE)
    #     # p = subprocess.Popen(['tail', '-f', filename], shell=True, stdout=subprocess.PIPE)
    #     output, err = p.communicate()
    #     for line in output.splitlines():
    #         if re.search(b'error|critical|fail', line.lower()):
    #             print(line)
    #             socketio.emit('new_log', {'data': line.decode()})
    log_data = read_logs()  # 获取日志
    # 判断如果此次获取日志行数减去上一次获取日志行数大于0，代表获取到新的日志
    if len(log_data) - line_number[0] > 0:
        log_type = 2  # 当前获取到日志
        log_difference = len(log_data) - line_number[0]  # 计算获取到少行新日志
        log_list = []  # 存放获取到的新日志
        # 遍历获取到的新日志存放到log_list中
        for i in range(log_difference):
            log_i = log_data[-(i + 1)].decode('utf-8')  # 遍历每一条日志并解码
            log_list.insert(0, log_i)  # 将获取的日志存放log_list中
    else:
        log_type = 3
        log_list = ''
    # 已字典形式返回前端
    _log = {
        'log_type': log_type,
        'log_list': log_list
    }
    line_number.pop()  # 删除上一次获取行数
    line_number.append(len(log_data))  # 添加此次获取行数
    socketio.emit('new_log', {'data': _log})
    print(_log)


if __name__ == '__main__':
    line_number = [0]  # 存放当前日志行数

    # socketio.run(app, debug=True)
    socketio.run(app, host='127.0.0.1', debug=True, port=5000, log_output=True)
    while True:
        my_log_()
        socketio.emit('new_log', {'data': 'New log'})
