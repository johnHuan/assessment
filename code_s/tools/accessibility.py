# coding=utf-8
# @Time : 2024/6/20 14:45
# @Author : Trifurs
# @File : accessibility.py
# @Software : PyCharm


import arcpy
import os
from data_manager import add_field, polygon2point


def feature_buffer(feature_file, buffer_file, buffer_distance):
    """
    给点要素设置缓冲区
    :param feature_file: 输入要素数据
    :param buffer_file: 输出缓冲区数据
    :param buffer_distance: 缓冲距离 单位 米
    :return:
    """
    buffer_distance = str(buffer_distance) + " meter"
    arcpy.Buffer_analysis(feature_file, buffer_file, buffer_distance, "FULL", "ROUND", "NONE")


def get_buffer_level(points_file, buffer_file, intersect_file, buffer_dis, buffer_level_dict):
    """
    计算点要素位于多少个要素的缓冲区内，并根据缓冲距离加权计分
    :param points_file: 输入点要素数据
    :param buffer_file: 输入缓冲区数据
    :param intersect_file: 点要素与缓冲区相交输出数据
    :param buffer_dis: 缓冲区距离
    :param buffer_level_dict: 点要素已有的得分字典
    :return: 更新后的点要素得分字典
    """
    arcpy.Intersect_analysis([points_file, buffer_file], intersect_file, "ALL", "", "")

    distance_weight = 1000.0 / float(buffer_dis)  # 单位是m
    # print(distance_weight)

    fc_rows = arcpy.SearchCursor(intersect_file)
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        if fc_row.Temp1 not in buffer_level_dict.keys():
            buffer_level_dict[fc_row.Temp1] = (distance_weight * 1.0)
        else:
            buffer_level_dict[fc_row.Temp1] += (distance_weight * 1.0)
    del fc_rows

    return buffer_level_dict


def update_polygon(polygons_file, buffer_num_dict, count_id="CCCID", count_name="BNUM"):
    """
    更新地块文件的属性
    :param polygons_file: 输入地块数据
    :param buffer_num_dict: 输入地块缓冲区得分
    :param count_id: 给定地块的标识符字段名
    :param count_name: 给定地块的缓冲区得分属性字段名
    :return:
    """
    fc_rows1 = arcpy.UpdateCursor(polygons_file)
    while True:
        fc_row1 = fc_rows1.next()
        if not fc_row1:
            break
        if fc_row1.Temp1 in buffer_num_dict.keys():
            fc_row1.Temp2 = buffer_num_dict[fc_row1.Temp1]
        else:
            fc_row1.Temp2 = 0.0
        fc_rows1.updateRow(fc_row1)
    del fc_rows1

    add_field(polygons_file, count_id, 'LONG')
    add_field(polygons_file, count_name, 'DOUBLE')

    arcpy.CalculateField_management(in_table=polygons_file, field=count_id, expression="!Temp1!",
                                    expression_type="PYTHON_9.3", code_block="")
    arcpy.CalculateField_management(in_table=polygons_file, field=count_name, expression="!Temp2!",
                                    expression_type="PYTHON_9.3", code_block="")


def get_accessibility(polygons_file, station_file, buffer_distance, temp_file, count_id="CCCID", count_name="BNUM"):
    """
    计算简化后的可达性指标
    :param polygons_file: 输入地块数据
    :param station_file: 输入待计算的点数据（消防站、垃圾收集站、垃圾转运站）
    :param buffer_distance: 缓冲距离 列表
    :param temp_file: 临时文件夹位置
    :param count_id: 给定地块的标识符字段名
    :param count_name: 给定地块的缓冲区得分属性字段名
    :return:
    """
    points_file = os.path.join(temp_file, "center_points.shp")
    buffer_file = os.path.join(temp_file, "buffers.shp")
    intersect_file = os.path.join(temp_file, "intersects.shp")

    polygon2point(polygons_file, points_file)
    buffer_num_dict = {}

    for dis in buffer_distance:
        feature_buffer(station_file, buffer_file, dis)
        temp_dict = get_buffer_level(points_file, buffer_file, intersect_file, dis, buffer_num_dict)
        buffer_num_dict = temp_dict

    # print(buffer_num_dict)
    update_polygon(polygons_file, buffer_num_dict, count_id, count_name)

    # arcpy.DeleteField_management(polygons_file, "Temp1")
    # arcpy.DeleteField_management(polygons_file, "Temp2")
    arcpy.DeleteField_management(polygons_file, count_id)


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    polygons = r"D:\lb\myCode\accessibility_new\data\data_for_test\test.shp"
    stations = r"D:\lb\myCode\accessibility_new\data\data_for_test\fire_station_poi.shp"
    buffers = [100.0, 500.0, 1000.0, 2000.0, 5000.0]
    # get_accessibility(polygons, stations, buffers)
