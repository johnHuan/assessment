# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 11:49
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : background.py
from flask import session

from app import socketio
from generate_log import read_logs


def background_thread():
    configs = session['configs']
    log_file = configs['log_path']
    with open(log_file, "r") as f:
        while True:
            socketio.sleep(1)
            # t = random.randint(1, 100)
            # socketio.emit('message', {'data': t}, namespace='/conn_logging')
            # for line in f.readlines():
            #     print(line, '=-============-=-0--0')
            #     socketio.emit('message', {'data': line}, namespace='/conn_logging', callback=ack)
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
            line_number.pop()  # 删除上一次获取行数
            line_number.append(len(log_data))  # 添加此次获取行数
            socketio.emit('message', {'data': log_list}, namespace='/conn_logging', callback=ack)
