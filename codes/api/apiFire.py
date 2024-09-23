# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 10:49
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : apiFire.py
import pandas as pd
from flask import Blueprint, render_template, session, jsonify

from commons.utils import get_colorBar

fire_bp = Blueprint('fire', __name__, template_folder='templates', static_folder='static')


@fire_bp.route('/fire_index')
def index():
    # 1.1 消防设施分布图
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 消防设施分布图"
    }
    return render_template('/1/item_index.html', **kwargs)


@fire_bp.route('/get_fire_fight_services')
def get_fire_fight_services():
    configs = session['configs']
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


@fire_bp.route('/fire_list')
def fire_list():
    # 1.2 消防设施列表
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 消防设施列表"
    }
    return render_template('/1/item_list.html', **kwargs)


@fire_bp.route('/fire_access')
def access():
    # 1.6 可达性评估
    key = 'nS1'
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
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 供给-可达性",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_ability')
def ability():
    # 1.7 消防站能力
    key = 'nS2'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 供给-消防站能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_given')
def given():
    # 1.4 消防供给评估
    key = 'nS'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 供给能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_pop_density')
def pop_density():
    # 1.7 人口密度
    key = 'nN1'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 需求-人口密度",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_buildings')
def fire_buildings():
    # 1.7 人口密度
    key = 'nN2'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 需求-建筑消防风险",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_risk')
def fire_risk():
    # 1.7 人口密度
    key = 'nN3'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 需求-危险设施风险",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_demand')
def fire_demand():
    # 1.7 人口密度
    key = 'nN'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 需求-消防需求能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)


@fire_bp.route('/fire_service')
def fire_service():
    # 1.7 人口密度
    key = 'nC'
    configs = session.get('configs')
    gdf = pd.read_csv(configs['gdf_path'], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 1,
        "page_loc": "消防能力现状评估 / 综合-消防服务能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/1/fire_templates.html', **kwargs)
