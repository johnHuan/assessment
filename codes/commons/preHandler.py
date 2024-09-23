# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 11:47
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : preHandler.py
import json

import pandas as pd
import shapefile
import yaml
from flask import session

from commons.coord import coord_convert
from logging_ import logging_
import pickle


def pre_handler():
    with open('info.json', 'r') as info:
        info_data = json.load(info)
    session['group_fire'] = info_data['key_value_name'][0]['group_fire']
    session['group_san'] = info_data['key_value_name'][1]['group_san']
    session['group_fire_valuation'] = info_data['key_value_name'][2]['group_fire_valuation']
    session['group_san_valuation'] = info_data['key_value_name'][3]['group_san_valuation']

    with open('configs.yaml', 'r') as config:
        conf_content = config.read()
    configs = yaml.safe_load(conf_content)
    session['configs'] = configs


# :flag [ planing, valuation ]表示消防和环卫哪种类型
def pre_gdf(flag):
    with open('configs.yaml', 'r') as config:
        conf_content = config.read()
    configs = yaml.safe_load(conf_content)
    _path = configs['log_path']
    log = logging_(_path).logger  # 实例化封装类
    log.info("读取配置文件")
    fire_shp = configs['shp_path'][flag]
    spr = shapefile.Reader(fire_shp)
    fields = []
    flds = spr.fields[1:]
    for field in flds:
        fields.append(str(field[0]))
    fields.append('boundary_84')  # 添加边界属性
    df_boundary = pd.DataFrame(columns=fields)
    for r in range(0, spr.numRecords):
        row = spr.record(r)
        row.append(spr.shape(r).points)
        row_data = []
        for col_index in range(0, len(row)):
            row_data.append(row[col_index])
        df_boundary.loc[r] = row_data
    spr.close()
    gdf = df_boundary
    gdf = gdf.drop('boundary_84', axis=1)
    parts = gdf.shape[0]
    boundary_84 = df_boundary.boundary_84.values.tolist()
    boundary = coord_convert(boundary_84, parts, configs)  # 热启动1
    gdf['boundary'] = boundary  # 热启动2
    gdf.to_csv(configs['gdf_path'][flag])
    return gdf