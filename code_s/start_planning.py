# coding=utf-8
# @Time : 2024/7/9 16:05
# @Author : Trifurs
# @File : start_planning.py
# @Software : PyCharm


import gc
import os
import time

import arcpy

from fire_service.planning.fire_planning import Fire_SNC
from sanitation_service.planning.sanitation_planning import Sanitation_SNC
from tools.data_prepare import Planning_Preparation
from tools.file_helper import read_configs, del_temp_file


def execute_planning():
    time_start = time.time()  # 记录开始时间
    arcpy.env.overwriteOutput = True  # 允许覆盖原有数据  ！！！非常重要！！！

    # config_file = r"configs.yaml"  # 配置文件路径
    config_file = r"configs.yaml"  # 配置文件路径
    config_dict = read_configs(config_file)  # 读取配置文件

    del_temp_file(config_dict['directories']["temp_file_planning"])  # 删除临时文件夹中现有数据

    pp = Planning_Preparation(config_dict)  # 数据预处理
    del pp
    gc.collect()

    ss = Sanitation_SNC(config_dict)  # 环卫服务能力评估
    del ss
    gc.collect()

    fs = Fire_SNC(config_dict)  # 消防服务能力评估
    del fs
    gc.collect()

    # 将计算完成的地块文件复制到结果文件夹
    arcpy.CopyFeatures_management(config_dict['shp_path']["polygons_for_planning"],
                                  os.path.join(config_dict['directories']["result_file"], "planning_result.shp"))

    print("计算结果保存在：")
    print(os.path.join(config_dict['directories']["result_file"], "planning_result.shp"))

    time_end = time.time()  # 记录结束时间
    time_sum = time_end - time_start  # 计算的时间差为程序的执行时间，单位为秒/s
    print("程序运行总时间：")
    print(time_sum)


if __name__ == '__main__':
    execute_planning()
