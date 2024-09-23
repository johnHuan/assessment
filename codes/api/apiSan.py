# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 10:49
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : apiSan.py
import pandas as pd
from flask import Blueprint, session, render_template, jsonify
from commons.utils import get_colorBar

san_bp = Blueprint('san', __name__, template_folder='templates', static_folder='static')


@san_bp.route('/san_dist')
def san_dist():
    # 环卫设施分布图
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 环卫设施分布图"
    }
    return render_template('/2/item_san_dist.html', **kwargs)


@san_bp.route('/san_list')
def san_list():
    #  环卫设施列表
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 环卫设施列表"
    }
    return render_template('/2/item_san_list.html', **kwargs)


@san_bp.route('/get_sanitation')
def get_sanitation():
    configs = session['configs']
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


@san_bp.route('/san_collection')
def san_collection():
    # 2.6 收集能力
    key = 'nS1_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 供给-收集能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)


@san_bp.route('/san_transfer')
def san_transfer():
    # 2.6 收集能力
    key = 'nS2_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 供给-转运能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)


@san_bp.route('/san_given')
def san_given():
    # 2.6 收集能力
    key = 'nS_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 供给能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)


@san_bp.route('/san_citizen')
def san_citizen():
    # 2.6 收集能力
    key = 'nN1_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 常住人口垃圾产量",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)


@san_bp.route('/san_service')
def san_service():
    # 2.6 收集能力
    key = 'nN2_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 服务人口垃圾产量",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)


@san_bp.route('/san_demand')
def san_demand():
    # 2.6 收集能力
    key = 'nN_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 环卫服务需求",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)


@san_bp.route('/san_ability')
def san_ability():
    # 2.6 收集能力
    key = 'nC_'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 2,
        "page_loc": "环卫能力现状评估 / 环卫服务能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/2/san_templates.html', **kwargs)
