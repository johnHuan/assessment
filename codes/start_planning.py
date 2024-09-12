# coding=utf-8
# @Time : 2024/7/9 16:05
# @Author : Trifurs
# @File : start_planning.py
# @Software : PyCharm


import gc
import os
import time

import arcpy
import yaml

from codes.index import socketio
from logging_ import logging_
from fire_service.planning.fire_planning import Fire_SNC
from sanitation_service.planning.sanitation_planning import Sanitation_SNC
from tools.data_prepare import Planning_Preparation
from tools.file_helper import read_configs, del_temp_file


def execute_planning():
    with open('./configs.yaml', 'r') as f_y:
        content = f_y.read()
    configs = yaml.safe_load(content)
    _path = configs['log_path']

    log = logging_(_path).logger  # 实例化封装类
    time_start = time.time()  # 记录开始时间
    arcpy.env.overwriteOutput = True  # 允许覆盖原有数据  ！！！非常重要！！！

    config_file = r"configs.yaml"  # 配置文件路径
    config_dict = read_configs(config_file)  # 读取配置文件
    log.info("开始删除临时文件")
    socketio.emit('message', {'data': '开始删除临时文件'}, namespace='/conn_logging')

    del_temp_file(config_dict['directories']["temp_file_planning"])  # 删除临时文件夹中现有数据
    log.info("删除临时文件完成")
    socketio.emit('message', {'data': '删除临时文件完成'}, namespace='/conn_logging')
    log.info("开始基础数据准备！")
    pp = Planning_Preparation(config_dict)  # 数据预处理
    log.info("基础数据准备完成！")
    del pp
    gc.collect()

    log.info("开始进行环卫服务能力评估！")
    ss = Sanitation_SNC(config_dict)  # 环卫服务能力评估
    log.info("环卫服务能力评估 完成！")
    del ss
    gc.collect()

    log.info("开始进行消防服务能力评估！")
    fs = Fire_SNC(config_dict)  # 消防服务能力评估
    log.info("消防服务能力评估完成！")
    del fs
    gc.collect()

    # 将计算完成的地块文件复制到结果文件夹
    arcpy.CopyFeatures_management(config_dict['shp_path']["polygons_for_planning"],
                                  os.path.join(config_dict['directories']["result_file"], "planning_result.shp"))

    # print("计算结果保存在：")
    # print(os.path.join(config_dict['directories']["result_file"], "planning_result.shp"))
    log.info("计算结果保存在：")
    log.info(os.path.join(config_dict['directories']["result_file"], "planning_result.shp"))

    time_end = time.time()  # 记录结束时间
    time_sum = time_end - time_start  # 计算的时间差为程序的执行时间，单位为秒/s
    log.info("程序运行总时间：")
    log.info(time_sum)


if __name__ == '__main__':
    execute_planning()
