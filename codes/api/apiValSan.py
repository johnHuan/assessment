# -*- coding: utf-8 -*-
# @Time    : 2024/9/22 10:49
# @Author  : Zhang Huan
# @Email   : johnhuan@whu.edu.cn
# QQ       : 248404941
# @File    : apiValSan.py
import json
import os

import pandas as pd
from flask import Blueprint, session, render_template, request

from commons.preHandler import pre_gdf
from commons.utils import get_colorBar

valSan_bp = Blueprint('valSan', __name__, template_folder='templates', static_folder='static')


@valSan_bp.route('/san_evaluating')
def san_evaluating():
    # 4 环卫评估
    with open('info.json', 'r') as fcc_file:
        json_data = json.load(fcc_file)
    required_file = json_data["required_file"]
    kwargs = {
        "menu_group": 4,
        "page_loc": "规划地块环卫能力 / 规划地块上传",
        "required_file": required_file
    }
    return render_template('/4/item_san_evaluating.html', **kwargs)


@valSan_bp.route('/san_upload_do', methods=['POST'])
def san_upload_do():
    configs = session.get('configs')
    f = request.files.get('file')
    filename = os.path.join(configs['upload_path']['san'], f.filename)
    f.save(filename)
    return {'flag': True}


@valSan_bp.route('/san_evaluating_do', methods=['GET'])
def san_evaluating_do():
    configs = session.get('configs')
    start_valuation_path = os.path.join(configs['planning_path'], 'start_valuation.py')
    command = 'python ' + start_valuation_path
    res = os.system(command)
    return {
        "status": True,
        "res": res
    }


@valSan_bp.route('/val_san_given')
def val_san_given():
    key = 'nS_'
    flag = 'valuation'
    is_valuation = session.get('valuation')
    configs = session.get('configs')
    if not is_valuation:  # 如果还没有评估就写csv
        gdf = pre_gdf(flag)
    else:  # 否则已经评估了就直接读取csv
        gdf = pd.read_csv(configs['gdf_path'][flag], index_col=0)
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
        "page_loc": "规划地块消防能力 / 供给能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/4/val_san.html', **kwargs)


@valSan_bp.route('/val_san_demand')
def val_san_demand():
    key = 'nN_'
    flag = 'valuation'
    is_valuation = session.get('valuation')
    configs = session.get('configs')
    if not is_valuation:  # 如果还没有评估就写csv
        gdf = pre_gdf(flag)
    else:  # 否则已经评估了就直接读取csv
        gdf = pd.read_csv(configs['gdf_path'][flag], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 4,
        "page_loc": "规划地块消防能力 / 需求能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/4/val_san.html', **kwargs)


@valSan_bp.route('/val_san_service')
def val_san_service():
    key = 'nC_'
    flag = 'valuation'
    is_valuation = session.get('valuation')
    configs = session.get('configs')
    if not is_valuation:  # 如果还没有评估就写csv
        gdf = pre_gdf(flag)
    else:  # 否则已经评估了就直接读取csv
        gdf = pd.read_csv(configs['gdf_path'][flag], index_col=0)
    parts = session['parts']
    gdf_sorted = gdf.sort_values(key)
    currentData = gdf_sorted[key].values.tolist()  # S1 值  可达性
    bdr = gdf_sorted['boundary'].values
    boundary_arr = []
    for i in range(0, parts):
        boundary_arr.append(eval(bdr[i]))
    colorbar = get_colorBar()
    kwargs = {
        "menu_group": 4,
        "page_loc": "规划地块消防能力 / 综合-服务能力",
        "boundary": boundary_arr,
        "currentData": currentData,
        "max_currentData": max(currentData),
        "min_currentData": min(currentData),
        "colorbar": colorbar
    }
    return render_template('/4/val_fire.html', **kwargs)
