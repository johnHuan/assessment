# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 11:45
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : coord.py
import json

import requests
from flask import session, jsonify


def coord_convert(boundary_84, parts, configs):
    boundary_arr = []
    for i in range(0, parts):
        boundary_len = len(boundary_84[i])
        coors = ''
        for j in range(0, boundary_len):
            coors += str(boundary_84[i][j][0]) + ',' + str(boundary_84[i][j][1]) + '|'
        middle_url = coors[:-1]
        base_url = configs['amap']['base_url']
        last_url = '&coordsys=gps'
        url = base_url + middle_url + last_url
        response = requests.request('get', url)
        dic = json.loads(response.text)
        boundary_elem = dic['locations'].split(';')
        bdr = []
        for k in range(0, boundary_len):
            pt_str = boundary_elem[k].split(',')
            bdr.append([float(pt_str[0]), float(pt_str[1])])
        boundary_arr.append(bdr)
    return boundary_arr
