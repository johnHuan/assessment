# -*- coding: utf-8 -*-
# @Time    : 2024/8/15 12:23
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : index.py
import json
import os.path
import sys  # reload()之前必须要引入模块
import random
from threading import Lock

import pandas as pd
import requests
import shapefile
import yaml
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, disconnect

from codes.generate_log import read_logs
from logging_ import logging_

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pmzzh!'
socketio = SocketIO(app)
async_mode = None
thread = None
thread_lock = Lock()


# api = Api(app)


@app.route('/')
def empty():
    # 1.1 默认缺省方法 直接定向到 消防设施分布图
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防设施分布图"
    }
    #                       /1/item_index.html
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
def fire_list():
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
    c = gdf_sorted.C.values.tolist()  # C 值 消防设施匹配度
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防匹配度评估",
        "boundarys": boundary_arr,
        "C": c,
        "max_c": max(c),
        "min_c": min(c),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_matching.html', **kwargs)


@app.route('/fire_given')
def given():
    # 1.4 消防供给评估
    gdf_sorted = gdf.sort_values('S')
    s = gdf_sorted.S.values.tolist()  # S 值 消防供给
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防供给评估",
        "boundarys": boundary_arr,
        "S": s,
        "max_s": max(s),
        "min_s": min(s),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_given.html', **kwargs)


@app.route('/fire_demand')
def demand():
    # 1.5 消防需求评估
    gdf_sorted = gdf.sort_values('N')
    n = gdf_sorted.N.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防需求评估",
        "boundarys": boundary_arr,
        "N": n,
        "max_n": max(n),
        "min_n": min(n),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_demand.html', **kwargs)


@app.route('/fire_access')
def access():
    # 1.6 可达性评估
    gdf_sorted = gdf.sort_values('S1')
    s1 = gdf_sorted.S1.values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 可达性评估",
        "boundarys": boundary_arr,
        "S1": s1,
        "max_S1": max(s1),
        "min_S1": min(s1),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_access.html', **kwargs)


@app.route('/fire_ability')
def ability():
    # 1.7 消防站能力
    gdf_sorted = gdf.sort_values('nS2')
    s2 = gdf_sorted.nS2.values.tolist()  # N1 值 消防站能力
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    color_bar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 消防站能力",
        "boundarys": boundary_arr,
        "S2": s2,
        "max_S2": max(s2),
        "min_S2": min(s2),
        "colorbar": color_bar
    }
    return render_template('/1/item_fire_ability.html', **kwargs)


@app.route('/fire_pop_density')
def pop_density():
    # 1.7 人口密度
    gdf_sorted = gdf.sort_values('N1')
    n1 = gdf_sorted.N1.values.tolist()  # N1 值 人口密度
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    color_bar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 人口密度",
        "boundarys": boundary_arr,
        "n1": n1,
        "max_n1": max(n1),
        "min_n1": min(n1),
        "colorbar": color_bar
    }
    return render_template('/1/item_fire_pop_density.html', **kwargs)


@app.route('/fire_build_density')
def build_density():
    # 1.8 建筑密度
    gdf_sorted = gdf.sort_values('N2')
    n2 = gdf_sorted.N2.values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 建筑密度",
        "boundarys": boundary_arr,
        "N2": n2,
        "max_N2": max(n2),
        "min_N2": min(n2),
        "colorbar": colorbar
    }
    return render_template('/1/item_fire_build_density.html', **kwargs)


@app.route('/fire_risk')
def build_risk():
    # 1.9 火灾风险评估
    gdf_sorted = gdf.sort_values('N3')
    n3 = gdf_sorted.N3.values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力 / 火灾风险评估",
        "boundarys": boundary_arr,
        "N3": n3,
        "max_N3": max(n3),
        "min_N3": min(n3),
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
    gdf_sorted = gdf.sort_values('C')
    c = gdf_sorted.C.values.tolist()  # C 值 消防设施匹配度
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫匹配度评估",
        "boundarys": boundary_arr,
        "C": c,
        "max_c": max(c),
        "min_c": min(c),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_matching.html', **kwargs)


@app.route('/san_given')
def san_given():
    # 2.4 环卫供给评估
    gdf_sorted = gdf.sort_values('S')
    s = gdf_sorted.S.values.tolist()  # S 值 消防供给
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫供给评估",
        "boundarys": boundary_arr,
        "S": s,
        "max_s": max(s),
        "min_s": min(s),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_given.html', **kwargs)


@app.route('/san_demand')
def san_demand():
    # 2.5 环卫需求评估
    gdf_sorted = gdf.sort_values('N_')
    n_ = gdf_sorted.N_.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 环卫需求评估",
        "boundarys": boundary_arr,
        "N": n_,
        "max_n": max(n_),
        "min_n": min(n_),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_demand.html', **kwargs)


@app.route('/san_collection')
def san_collection():
    # 2.6 收集能力
    gdf_sorted = gdf.sort_values('S12_')
    s12_ = gdf_sorted.S12_.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 收集能力",
        "boundarys": boundary_arr,
        "N": s12_,
        "max_n": max(s12_),
        "min_n": min(s12_),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_collection.html', **kwargs)


@app.route('/san_transfer')
def san_transfer():
    # 2.7 转运能力
    gdf_sorted = gdf.sort_values('S2_')
    s2_ = gdf_sorted.S2_.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 转运能力",
        "boundarys": boundary_arr,
        "N": s2_,
        "max_n": max(s2_),
        "min_n": min(s2_),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_transfer.html', **kwargs)


@app.route('/san_citizen')
def san_citizen():
    # 2.8 常驻人口
    gdf_sorted = gdf.sort_values('N1_')
    n1_ = gdf_sorted.N1_.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 常驻人口",
        "boundarys": boundary_arr,
        "N": n1_,
        "max_n": max(n1_),
        "min_n": min(n1_),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_citizen.html', **kwargs)


@app.route('/san_service')
def san_service():
    # 2.9 服务人口
    gdf_sorted = gdf.sort_values('N')
    n = gdf_sorted.N.values.tolist()  # N 值 消防需求
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(bdr[i])
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力 / 服务人口",
        "boundarys": boundary_arr,
        "N": n,
        "max_n": max(n),
        "min_n": min(n),
        "colorbar": colorbar
    }
    return render_template('/2/item_san_service.html', **kwargs)


@app.route('/fire_evaluating')
def fire_evaluating():
    # 3 消防评估
    with open('info.json', 'r') as fcc_file:
        json_data = json.load(fcc_file)
    required_file = json_data["required_file"]
    kwargs = {
        "menu_group": 3,
        "page_loc": "消防规划评估",
        "required_file": required_file
    }
    return render_template('/3/item_fire_evaluating.html', **kwargs)


@app.route('/san_evaluating')
def san_evaluating():
    # 4 环卫评估
    with open('info.json', 'r') as fcc_file:
        json_data = json.load(fcc_file)
    required_file = json_data["required_file"]
    kwargs = {
        "menu_group": 4,
        "page_loc": "环卫规划评估",
        "required_file": required_file
    }
    return render_template('/4/item_san_evaluating.html', **kwargs)


@app.route('/get_fire_fire_fight_services')
def get_fire_fire_fight_services():
    df_fire = pd.read_excel(configs['excel_path']['fire_path'], usecols=["名称", "经度", "纬度"])
    _data = []
    for i, record in df_fire.iterrows():
        _data.append({
            "id": str(i + 1),
            'names': record[u'名称'],
            'loc': [record[u'经度'], record[u'纬度']]
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
    filename = os.path.join(configs['upload_path']['fire'], f.filename)
    f.save(filename)
    return {'flag': True}


@app.route('/san_upload_do', methods=['POST'])
def san_upload_do():
    f = request.files.get('file')
    filename = os.path.join(configs['upload_path']['san'], f.filename)
    f.save(filename)
    return {'flag': True}


@app.route('/fire_evaluating_do', methods=['GET'])
def fire_evaluating_do():
    start_planning_path = os.path.join(configs['planning_path'], 'start_planning.py')
    command = 'python ' + start_planning_path
    res = os.system(command)
    return {
        "status": True,
        "res": res
    }


@app.route('/san_evaluating_do', methods=['GET'])
def san_evaluating_do():
    start_planning_path = os.path.join(configs['planning_path'], 'start_valuation.py')
    command = 'python ' + start_planning_path
    res = os.system(command)
    return {
        "status": True,
        "res": res
    }


@app.route('/get_sanitation')
def get_sanitation():
    df_san = pd.read_excel(configs['excel_path']['san_path'], usecols=["地址", "名称", "经度", "纬度"])
    _data = []
    for i, record in df_san.iterrows():
        _data.append({
            "id": str(i + 1),
            'names': record[u'名称'],
            'address': record[u'地址'],
            'loc': [record[u'经度'], record[u'纬度']]
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


def get_colorBar():
    color_bar = []  # colorbar 三色数组, 从 RGB(255, 0, 0) 渐变到 RGB(0, 0, 255)
    for i in range(0, parts):
        # 获取 红->蓝 渐变色
        red = 255 + (0 - 255) / parts * i
        green = 0
        blue = 0 + (255 - 0) / parts * i
        color_bar.append([red, green, blue])
    return color_bar


def coord_convert():
    boundary_arr = []
    boundary_84 = gdf.boundary_84.values.tolist()
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


def ack():
    # 似乎无用
    print('message was received!')


# 关闭时
@socketio.on('disconnect_request', namespace='/conn_logging')
def disconnect_request():
    print('Client disconnected')
    disconnect()


@socketio.on("fuck", namespace="/conn_logging")
def fuck(fuck):
    print('received message: ' + str(fuck))


# 连接时
@socketio.on('connect', namespace='/conn_logging')
def connect():
    global thread
    socketio.emit('message',
                  {'data': "已经成功创建连接!"}, namespace='/conn_logging', callback=ack)
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


def background_thread():
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


if __name__ == '__main__':
    line_number = [0]  # 存放当前日志行数
    with open('configs.yaml', 'r') as f_y:
        content = f_y.read()
    configs = yaml.safe_load(content)
    _path = configs['log_path']
    log = logging_(_path).logger  # 实例化封装类
    log.info("读取配置文件")

    fire_path = configs['shp_path']['fire_path']
    san_path = configs['shp_path']['san_path']
    fire_shp = configs['shp_path']['fire_shp']
    spr = shapefile.Reader(fire_shp)
    fields = []
    flds = spr.fields[1:]
    for field in flds:
        fields.append(str(field[0]))
    fields.append('boundary_84')  # 添加边界属性
    df = pd.DataFrame(columns=fields)
    for r in range(0, spr.numRecords):
        row = spr.record(r)
        row.append(spr.shape(r).points)
        row_data = []
        for col_index in range(0, len(row)):
            row_data.append(row[col_index])
        df.loc[r] = row_data
    spr.close()
    gdf = df
    parts = len(gdf)
    # boundary = coord_convert()  # 热启动
    # gdf['boundary'] = boundary  # 热启动

    # app.run(host='127.0.0.1', debug=True, port=5000)
    socketio.run(app, host='127.0.0.1', debug=True, port=5000)
