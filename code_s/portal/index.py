# -*- coding: utf-8 -*-
# @Time    : 2024/8/15 12:23
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : index.py
import json
import yaml
import pandas as pd
import requests
from flask import Flask, render_template, jsonify, request
from flask_restful import Api
import numpy as np

from geopandas.io.file import _read_file as read_file

app = Flask(__name__)
api = Api(app)


@app.route('/')
def empty():
    # 1.1 默认缺省方法 直接定向到 消防设施分布图
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防设施分布图"
    }
    return render_template('/1/item_index.html', **kwargs)


@app.route('/fire_index')
def index():
    # 1.1 消防设施分布图
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防设施分布图"
    }
    return render_template('/1/item_index.html', **kwargs)


@app.route('/fire_list')
def list():
    # 1.2 消防设施列表
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防设施列表"
    }
    return render_template('/1/item_list.html', **kwargs)


@app.route('/fire_matching')
def evaluate():
    # 1.3 消防匹配度评估
    gdf_sorted = gdf.sort_values('C')
    C = gdf_sorted.C.values.tolist()  # C 值 消防设施匹配度
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防匹配度评估",
        "boundarys": boundarys,
        "C": C,
        "max_c": max(C),
        "min_c": min(C),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_matching.html', **kwargs)


@app.route('/fire_given')
def given():
    # 1.4 消防供给评估
    gdf_sorted = gdf.sort_values('S')
    S = gdf_sorted.S.values.tolist()  # S 值 消防供给
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防供给评估",
        "boundarys": boundarys,
        "S": S,
        "max_s": max(S),
        "min_s": min(S),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_given.html', **kwargs)


@app.route('/fire_demand')
def demand():
    # 1.5 消防需求评估
    gdf_sorted = gdf.sort_values('N')
    N = gdf_sorted.N.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防需求评估",
        "boundarys": boundarys,
        "N": N,
        "max_n": max(N),
        "min_n": min(N),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_demand.html', **kwargs)


@app.route('/fire_access')
def access():
    # 1.6 可达性评估
    gdf_sorted = gdf.sort_values('S1')
    S1 = gdf_sorted.S1.values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 可达性评估",
        "boundarys": boundarys,
        "S1": S1,
        "max_S1": max(S1),
        "min_S1": min(S1),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_access.html', **kwargs)


@app.route('/fire_ability')
def ability():
    # 1.7 消防站能力
    gdf_sorted = gdf.sort_values('nS2')
    S2 = gdf_sorted.nS2.values.tolist()  # N1 值 消防站能力
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防站能力",
        "boundarys": boundarys,
        "S2": S2,
        "max_S2": max(S2),
        "min_S2": min(S2),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_ability.html', **kwargs)


@app.route('/fire_pop_density')
def pop_density():
    # 1.7 人口密度
    gdf_sorted = gdf.sort_values('N1')
    n1 = gdf_sorted.N1.values.tolist()  # N1 值 人口密度
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 人口密度",
        "boundarys": boundarys,
        "n1": n1,
        "max_n1": max(n1),
        "min_n1": min(n1),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_pop_density.html', **kwargs)


@app.route('/fire_build_density')
def build_density():
    # 1.8 建筑密度
    gdf_sorted = gdf.sort_values('N2')
    N2 = gdf_sorted.N2.values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 建筑密度",
        "boundarys": boundarys,
        "N2": N2,
        "max_N2": max(N2),
        "min_N2": min(N2),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_build_density.html', **kwargs)


@app.route('/fire_risk')
def build_risk():
    # 1.9 火灾风险评估
    gdf_sorted = gdf.sort_values('N3')
    N3 = gdf_sorted.N3.values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundarys = []
    for i in range(0, parts):
        boundarys.append(bdr[i])
    colorbar = get_colorbar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 火灾风险评估",
        "boundarys": boundarys,
        "N3": N3,
        "max_N3": max(N3),
        "min_N3": min(N3),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_risk.html', **kwargs)


@app.route('/san_dist')
def san_dist():
    # 2.1 环卫设施分布图
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫设施分布图"
    }
    return render_template('/2/item_san_dist.html', **kwargs)


@app.route('/san_list')
def san_list():
    # 2.2 环卫设施列表
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫设施列表"
    }
    return render_template('/2/item_san_list.html', **kwargs)


@app.route('/san_matching')
def san_matching():
    # 2.3 环卫匹配度评估
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫匹配度评估"
    }
    return render_template('/2/item_san_matching.html', **kwargs)


@app.route('/san_given')
def san_given():
    # 2.4 环卫供给评估
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫供给评估"
    }
    return render_template('/2/item_san_given.html', **kwargs)


@app.route('/san_demand')
def san_demand():
    # 2.5 环卫需求评估
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫需求评估"
    }
    return render_template('/2/item_san_demand.html', **kwargs)


@app.route('/san_collection')
def san_collection():
    # 2.6 收集能力
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 收集能力"
    }
    return render_template('/2/item_san_collection.html', **kwargs)


@app.route('/san_transfer')
def san_transfer():
    # 2.7 转运能力
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 转运能力"
    }
    return render_template('/2/item_san_transfer.html', **kwargs)


@app.route('/san_citizen')
def san_citizen():
    # 2.8 常驻人口
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 常驻人口"
    }
    return render_template('/2/item_san_citizen.html', **kwargs)


@app.route('/san_service')
def san_service():
    # 2.9 服务人口
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 服务人口"
    }
    return render_template('/2/item_san_service.html', **kwargs)


@app.route('/fire_upload')
def saneva():
    # 3.1 地块上传
    kwargs = {
        "menu_group": 3,
        "page_loc": "消防规划评估 / 地块上传"
    }
    return render_template('/3/item_fire_upload.html', **kwargs)


@app.route('/fire_evaluating')
def fire_evaluating():
    # 3.2 开始评估
    kwargs = {
        "menu_group": 3,
        "page_loc": "消防规划评估 / 开始评估"
    }
    return render_template('/3/item_fire_evaluating.html', **kwargs)


@app.route('/san_upload')
def san_upload():
    # 4.1 开始评估
    kwargs = {
        "menu_group": 4,
        "page_loc": "环卫规划评估 / 地块上传"
    }
    return render_template('/4/item_san_upload.html', **kwargs)


@app.route('/san_evaluating')
def san_evaluating():
    # 4.2 开始评估
    kwargs = {
        "menu_group": 4,
        "page_loc": "环卫规划评估 / 开始评估"
    }
    return render_template('/4/item_san_evaluating.html', **kwargs)


@app.route('/get_fire_fire_fight_services')
def get_fire_fire_fight_services():
    df = pd.read_excel(configs['excel_path']['fire_path'], usecols=["名称", "经度", "纬度"])
    _data = []
    for i, r in df.iterrows():
        _data.append({
            "id": str(i + 1),
            'names': r[u'名称'],
            'loc': [r[u'经度'], r[u'纬度']]
        })
    data = {
        "code": 0,
        'count': len(_data),
        'info': '武汉消防设施列表',
        'data': _data
    }

    return jsonify(data)


@app.route('/fire_upload_do', methods=['POST'])
def fire_upload_do():
    f = request.files.get('file')
    f.save(configs['upload_path']['san'] + str(f.filename))
    return {'flag': True}


@app.route('/san_upload_do', methods=['POST'])
def san_upload_do():
    f = request.files.get('file')
    f.save(configs['upload_path']['san'] + str(f.filename))
    return {'flag': True}


@app.route('/get_sanitation')
def get_sanitation():
    file_path = configs['excel_path']['san_path']
    df = pd.read_excel(fire_path, usecols=["地址", "名称", "经度", "纬度"])
    _data = []
    for i, r in df.iterrows():
        _data.append({
            "id": str(i + 1),
            'names': r[u'名称'],
            'address': r[u'地址'],
            'loc': [r[u'经度'], r[u'纬度']]
        })
    data = {
        "code": 0,
        'count': len(_data),
        'info': '武汉环卫设施列表',
        'data': _data
    }
    return jsonify(data)


@app.template_filter("get_action")
def get_action(x):
    y = str(x).split('/')
    if len(y[-1]) == 0:
        return 'fire_index'
    return y[-1]


def get_colorbar():
    colorbar = []  # colorbar 三色数组, 从 RGB(255, 0, 0) 渐变到 RGB(0, 0, 255)
    for i in range(0, parts):
        # 获取 红->蓝 渐变色
        r = 255 + (0 - 255) / parts * i
        g = 0
        b = 0 + (255 - 0) / parts * i
        colorbar.append([r, g, b])
    return colorbar


def coord_convert():
    boundarys = []
    for i in range(0, parts):
        polygon = np.array(gdf.geometry.boundary[i].xy).tolist()
        boundary_len = len(polygon[0])
        coors = ''
        for j in range(0, boundary_len):
            coors += str(polygon[0][j]) + ',' + str(polygon[1][j]) + '|'
        middle_url = coors[:-1]
        base_url = configs['amap']['base_url']
        last_url = '&coordsys=gps'
        url = base_url + middle_url + last_url
        response = requests.request('get', url)
        map = json.loads(response.text)
        boundary = map['locations'].split(';')
        bdr = []
        for k in range(0, boundary_len):
            pt_str = boundary[k].split(',')
            bdr.append([float(pt_str[0]), float(pt_str[1])])
        boundarys.append(bdr)
    return boundarys


if __name__ == '__main__':
    with open('../configs.yaml', 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    configs = yaml.safe_load(content)
    fire_path = configs['shp_path']['fire_path']
    san_path = configs['shp_path']['san_path']
    fire_shp = configs['shp_path']['fire_shp']
    gdf = read_file(fire_shp)
    gdf = gdf.fillna(0)
    parts = len(gdf)
    boundary = coord_convert()   # 热启动
    gdf['boundary'] = boundary   # 热启动
    app.run()
