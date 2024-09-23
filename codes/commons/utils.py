# -*- coding: utf-8 -*-
# @Time    : 2024/9/23 8:42
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : utils.py
from flask import session


def get_colorBar():
    parts = session['parts']
    color_bar = []  # colorbar 三色数组, 从 RGB(255, 0, 0) 渐变到 RGB(0, 0, 255)
    for i in range(0, parts):
        # 获取 红->蓝 渐变色
        red = 255 + (0 - 255) / parts * i
        green = 0
        blue = 0 + (255 - 0) / parts * i
        color_bar.append([red, green, blue])
    return color_bar


