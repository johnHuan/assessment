# coding=utf-8
# @Time : 2024/7/16 15:34
# @Author : Trifurs
# @File : accessibility_road.py
# @Software : PyCharm


import arcpy
import math
import os
from data_manager import create_gdb


def compute_OD(temp_dir, origin_poi, destination_poi, roads, cut_off):
    """
    根据路网计算OD成本矩阵
    :param temp_dir: 临时文件夹
    :param origin_poi: 起点文件
    :param destination_poi: 终点文件
    :param roads: 路网文件
    :param cut_off: 距离限制（单位：km） 尽量大一点，后续计算会挑选最近的点
    :return: 起点-终点 线要素数据集
    """
    od_gdb = create_gdb(temp_dir)
    arcpy.na.GenerateOriginDestinationCostMatrix(
        origin_poi, destination_poi, roads, od_gdb,
        Cutoff=cut_off, Origin_Destination_Line_Shape='STRAIGHT_LINES',
        Output_Origins_Name='Origins', Output_Destinations_Name='Destinations',
        Output_Origin_Destination_Lines_Name='Lines')

    arcpy.env.workspace = od_gdb
    fcs = arcpy.ListFeatureClasses()
    ODLine = ''
    for fc in fcs:
        # print(fc)
        if fc == "Lines":
            ODLine = fc
            break
        else:
            continue

    return ODLine


def compute_time(temp_dir, origin_poi, destination_poi, roads, cut_off=10.0):
    """
    计算距离最短的OD对
    :param temp_dir: 临时文件夹
    :param origin_poi: 起点文件
    :param destination_poi: 终点文件
    :param roads: 路网文件
    :param cut_off: 距离限制（单位：km） 尽量大一点，后续计算会挑选最近的点
    :return: 距离最短的OD对 {OID: [DID, Distance], ...}
    """
    # flds = arcpy.ListFields(ODLine)
    # for fld in flds:
    #     print(fld.name, fld.type, fld.length)

    od_dict = {}
    ODLine = compute_OD(temp_dir, origin_poi, destination_poi, roads, cut_off)
    fc_rows = arcpy.SearchCursor(ODLine)
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        if fc_row.OriginOID not in od_dict.keys():
            od_dict[fc_row.OriginOID] = [fc_row.DestinationOID, fc_row.Total_Distance]
        else:
            if od_dict[fc_row.OriginOID][1] > fc_row.Total_Distance:
                od_dict[fc_row.OriginOID] = [fc_row.DestinationOID, fc_row.Total_Distance]
    del fc_rows

    return od_dict


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    temp_dir0 = r"D:\lb\myCode\assessment\data\temp\valuation"
    origin_poi0 = r"D:\lb\myCode\assessment\data\temp\valuation\polygons_poi.shp"
    destination_poi0 = r"D:\lb\myCode\assessment\data\temp\valuation\fire_station_poi.shp"
    roads0 = r"D:\lb\myCode\assessment\data\data_for_test\roads\roads_cut_topo_ND.nd"

    od_dict0 = compute_time(temp_dir0, origin_poi0, destination_poi0, roads0)
    print(od_dict0)
