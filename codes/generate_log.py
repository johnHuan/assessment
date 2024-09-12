# -*- coding: utf-8 -*-
# @Time    : 2024/9/9 11:37
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : generate_log.py


# 导入上面封装好的日志输出
import time

import logging_
import os

_path = os.path.dirname(__file__)  # 获取当前文件路径


# 读取日志并返回
def read_logs():
    log_path = "%s/log.log" % _path  # 获取日志文件路径
    with open(log_path, 'rb') as f:
        log_size = os.path.getsize(log_path)  # 获取日志大小
        offset = -100
        # 如果文件大小为0时返回空
        if log_size == 0:
            return ''
        while True:
            # 判断offset是否大于文件字节数,是则读取所有行,并返回
            if abs(offset) >= log_size:
                f.seek(-log_size, 2)
                data = f.readlines()
                return data
            # 游标移动倒数的字节数位置
            data = f.readlines()
            # 判断读取到的行数，如果大于1则返回最后一行，否则扩大offset
            if len(data) > 1:
                return data
            else:
                offset *= 2


