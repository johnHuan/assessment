# coding=utf-8
# @Time : 2024/6/27 8:26
# @Author : Trifurs
# @File : file_helper.py
# @Software : PyCharm


import arcpy
import os
import pandas as pd
from data_manager import add_field


def del_temp_file(temp_path):
    """
    清空Temp临时文件夹
    :param temp_path: 临时文件夹路径
    :return:
    """
    ls = os.listdir(temp_path)
    for i in ls:
        c_path = os.path.join(temp_path, i)
        if os.path.isdir(c_path):  # 如果是文件夹那么递归调用一下
            del_temp_file(c_path)
        else:  # 如果是一个文件那么直接删除
            os.remove(c_path)
    print ('\n临时文件已清空完成！\n')


def read_configs(configs_file):
    """
    读取配置文件并转化为字典
    :param configs_file: 输入配置文件
    :return: 配置项字典
    """
    config_dict = {}
    with open(configs_file, 'r') as configs:
        for line in configs:
            if len(line.replace(" ", "")) < 4 or line[0] == "#":
                continue
            # print(len(line))
            config = line.split(": ")
            config_value = config[1].split("#")
            config_dict[config[0].replace(" ", "")] = config_value[0].replace(" ", "")
            if config[0] == "buffers" or config[0] == "hazard_buffers":
                buffer_list = []
                for dis in config_value[0].split(","):
                    buffer_list.append(float(dis))
                config_dict[config[0]] = buffer_list

    del configs
    print("配置文件读取完成：")
    for key in config_dict.keys():
        print("{}: {}".format(key, config_dict[key]))
    return config_dict


def get_fire_risk(excel_file, polygons_file):
    """
    读取用地消防风险系数表并将权重添加到地块文件
    :param excel_file: 输入Excel表格
    :param polygons_file: 输入地块文件
    :return:
    """
    df = pd.read_excel(excel_file)
    weight_dict = {}
    for row in range(df.shape[0]):
        weight_dict[int(df["N_DLBM"][row])] = df["Weight"][row]
    # print(weight_dict)

    add_field(polygons_file, "Risk", 'DOUBLE')

    fc_rows = arcpy.UpdateCursor(polygons_file)
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        # print(fc_row.N_DLBM)
        fc_row.Risk = weight_dict[int(fc_row.N_DLBM)]
        fc_rows.updateRow(fc_row)
    del fc_rows
    # print("  用地消防风险系数表读取完成！")


def get_per_area(excel_file, polygons_file):
    """
    读取人均服务占地面积表并将其添加到地块文件
    :param excel_file: 输入Excel表格
    :param polygons_file: 输入地块文件
    :return:
    """
    df = pd.read_excel(excel_file)
    per_dict = {}
    for row in range(df.shape[0]):
        per_dict[int(df["N_DLBM"][row])] = [df["CA_Per"][row], df["B_Types"][row]]
    # print(per_dict)

    add_field(polygons_file, "CA_Per", 'DOUBLE')
    add_field(polygons_file, "B_Types", 'TEXT')

    fc_rows = arcpy.UpdateCursor(polygons_file)
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        # print(fc_row.N_DLBM)
        fc_row.CA_Per = per_dict[int(fc_row.N_DLBM)][0]
        fc_row.B_Types = per_dict[int(fc_row.N_DLBM)][1]
        fc_rows.updateRow(fc_row)
    del fc_rows
    # print("  人均服务占地面积表读取完成！")


def get_n_extent(excel_file, polygons_file):
    """
    读取N指标计算范围并将其添加到地块文件
    :param excel_file: 输入Excel表格
    :param polygons_file: 输入地块文件
    :return:
    """
    df = pd.read_excel(excel_file)
    extent_dict = {}
    for row in range(df.shape[0]):
        extent_dict[int(df["N_DLBM"][row])] = [float(df["XF_N1"][row]),
                                               float(df["HW_N1"][row]),
                                               float(df["HW_N2"][row])]

    add_field(polygons_file, "XF_N1", 'DOUBLE')
    add_field(polygons_file, "HW_N1", 'DOUBLE')
    add_field(polygons_file, "HW_N2", 'DOUBLE')

    fc_rows = arcpy.UpdateCursor(polygons_file)
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        # print(fc_row.N_DLBM)
        # print(extent_dict)
        fc_row.XF_N1 = extent_dict[int(fc_row.N_DLBM)][0]
        fc_row.HW_N1 = extent_dict[int(fc_row.N_DLBM)][1]
        fc_row.HW_N2 = extent_dict[int(fc_row.N_DLBM)][2]
        fc_rows.updateRow(fc_row)
    del fc_rows


if __name__ == '__main__':
    excel_file0 = r"D:\lb\myCode\accessibility_new\data\data_for_test\tables\fire_risk_weights.xlsx"
    polygons_file0 = r"D:\lb\myCode\accessibility_new\data\data_for_test\polygons\test.shp"
    configs_file0 = r"D:\lb\myCode\accessibility_new\code\configs.yaml"
    get_fire_risk(excel_file0, polygons_file0)
    read_configs(configs_file0)
