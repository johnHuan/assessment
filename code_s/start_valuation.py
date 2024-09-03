# coding=utf-8
# @Time : 2024/7/9 16:05
# @Author : Trifurs
# @File : start_valuation.py
# @Software : PyCharm


import arcpy
import time
import os
from tools.file_helper import read_configs, del_temp_file
from tools.data_prepare import Valuation_Preparation
from fire_service.valuation.fire_valuation import Fire_SNC
from sanitation_service.valuation.sanitation_valuation import Sanitation_SNC


time_start = time.time()  # 记录开始时间
arcpy.env.overwriteOutput = True    # 允许覆盖原有数据  ！！！非常重要！！！

config_file = r"configs.yaml"   # 配置文件路径
config_dict = read_configs(config_file)     # 读取配置文件

del_temp_file(config_dict["temp_file"])     # 删除临时文件夹中现有数据
Valuation_Preparation(config_dict)  # 数据预处理
Fire_SNC(config_dict)   # 消防服务能力评估
Sanitation_SNC(config_dict)     # 环卫服务能力评估


# 将计算完成的地块文件复制到结果文件夹
arcpy.CopyFeatures_management(config_dict["polygons"],
                              os.path.join(config_dict["result_file"], "valuation_result.shp"))

print("计算结果保存在：")
print(os.path.join(config_dict["result_file"], "valuation_result.shp"))

time_end = time.time()  # 记录结束时间
time_sum = time_end - time_start  # 计算的时间差为程序的执行时间，单位为秒/s
print("程序运行总时间：")
print(time_sum)
