# coding=utf-8
# @Time : 2024/6/21 9:29
# @Author : Trifurs
# @File : data_manager.py
# @Software : PyCharm


import arcpy
import os
import sys

import yaml

from codes.logging_ import logging_

reload(sys)
sys.setdefaultencoding('utf8')
with open('./configs.yaml', 'r') as f_y:
    content = f_y.read()
configs = yaml.safe_load(content)
_path = configs['log_path']
log = logging_(_path).logger  # 实例化封装类


def get_year_risk(built_year):
    # print(built_year)

    if len(built_year.replace(" ", "")) == 0:
        return 1.0
    year_int = int(built_year[0: 4: 1])
    if year_int == 2000:
        if len(built_year) == 4:
            return 0.75
        elif "前" in built_year:
            return 1.0
        else:
            return 0.75
    elif 2000 < year_int <= 2005:
        return 0.75
    elif 2005 < year_int <= 2015:
        return 0.50
    elif year_int < 2000:
        return 1.0
    else:
        return 0.25

    # if "新建" in built_year:
    #     built_year = built_year.replace("新建", "")
    #
    # year_list = built_year.split("年")

    # if len(built_year.replace(" ", "")) == 0:
    #     return 1.0
    # elif int(year_list[0]) == 2000 and len(year_list) == 1:
    #     return 0.75
    # elif int(year_list[0]) == 2000 and year_list[1] == "前":
    #     return 1.0
    # elif int(year_list[0]) == 2000 and year_list[1] != "前":
    #     return 0.75
    # elif 2000 < int(year_list[0]) <= 2005:
    #     return 0.75
    # elif 2005 < int(year_list[0]) <= 2015:
    #     return 0.5
    # else:
    #     return 0.25


def get_fire_station_level(station_name):
    if "大队" in station_name:
        return 100
    elif "支队" in station_name:
        return 80
    elif "中队" in station_name or "救援站" in station_name:
        return 60
    elif "小型" in station_name:
        return 40
    elif "微站" in station_name:
        return 20
    else:
        return 40


def create_gdb(output_path, file_name="OD"):
    """
    创建OD成本矩阵的地理空间数据库
    :param output_path: 数据库所在位置
    :param file_name: 数据库名称
    :return: 生成数据库的路径
    """
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # arcpy.env.workspace = output_path
    # arcpy.env.overwriteOutput = True

    output_gdb = os.path.join(output_path, file_name + r".gdb")
    if not arcpy.Exists(output_gdb):
        arcpy.CreateFileGDB_management(output_path, file_name)

    return output_gdb


def list_normalize(input_list):
    """
    将列表的值标准化至[0, 100]
    :param input_list: 输入列表
    :return: 标准化后的列表
    """
    output_list = []
    list_max = max(input_list)
    list_min = min(input_list)
    for num in input_list:
        if list_min != list_max:
            num_normalized = 100 * (num - list_min) / (list_max - list_min)
            output_list.append(num_normalized)
        else:
            output_list.append(100)  # 如果所有值相等，则均赋值为100

    return output_list


def field_normalize(input_shp, field_name, new_name):
    """
    将矢量文件的某个字段标准化至[0, 100]
    :param input_shp: 输入矢量文件
    :param field_name: 需要标准化的字段
    :param new_name: 标准化后数据的新字段名称
    :return:
    """
    field_list = []

    add_field(input_shp, "Temp0", "DOUBLE")
    arcpy.CalculateField_management(in_table=input_shp, field="Temp0", expression="!" + field_name + "!",
                                    expression_type="PYTHON_9.3", code_block="")

    fc_rows = arcpy.SearchCursor(input_shp)
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        field_list.append(fc_row.Temp0)
    del fc_rows

    field_list = list_normalize(field_list)
    fc_rows = arcpy.UpdateCursor(input_shp)
    index = 0
    while True:
        fc_row = fc_rows.next()
        if not fc_row:
            break
        fc_row.Temp0 = field_list[index]
        fc_rows.updateRow(fc_row)
        index += 1
    del fc_rows

    add_field(input_shp, new_name, "DOUBLE")
    arcpy.CalculateField_management(in_table=input_shp, field=new_name, expression="!Temp0!",
                                    expression_type="PYTHON_9.3", code_block="")
    arcpy.DeleteField_management(input_shp, "Temp0")
    log.info("将矢量文件的某个字段标准化至[0, 100]")

def add_field(input_shp, field_name, field_type):
    """
    矢量文件添加字段
    :param input_shp: 输入矢量文件
    :param field_name: 字段名称
    :param field_type: 字段类型
    :return:
    """
    flds = arcpy.ListFields(input_shp)
    fld_NameList = []
    for fld in flds:
        fld_NameList.append(fld.name)

    if field_name in fld_NameList:
        arcpy.DeleteField_management(input_shp, field_name)
    arcpy.AddField_management(input_shp, field_name, field_type)


def select_feature_by_attribution(input_feature, select_express, selected_feature):
    """
    按属性选择要素并另存
    :param input_feature: 输入待筛选的要素
    :param select_express: 按属性选择的表达式
    :param selected_feature: 输出选定的要素
    :return:
    """
    arcpy.MakeFeatureLayer_management(input_feature, "lyr")
    arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", select_express)  # 按属性选择
    arcpy.CopyFeatures_management("lyr", selected_feature)
    arcpy.Delete_management("lyr")


def select_feature_by_location(input_feature, intersect_feature, selected_feature):
    """
    按属性选择要素并另存
    :param input_feature: 输入待筛选的要素
    :param intersect_feature: 与待筛选要素相交的要素
    :param selected_feature: 输出选定的要素
    :return:
    """
    arcpy.MakeFeatureLayer_management(input_feature, "lyr")
    arcpy.SelectLayerByLocation_management("lyr", "INTERSECT", intersect_feature)  # 按位置选择
    arcpy.CopyFeatures_management("lyr", selected_feature)
    arcpy.Delete_management("lyr")


def polygon2point(polygons_file, points_file, temp_id="Temp1", temp_num="Temp2"):
    """
    面要素转化为点要素
    :param polygons_file: 输入的面要素数据
    :param points_file: 输出的点要素数据
    :param temp_id: 面要素与点要素的关联字段
    :param temp_num: 空字段
    :return:
    """
    add_field(polygons_file, temp_id, 'LONG')
    add_field(polygons_file, temp_num, 'DOUBLE')
    arcpy.CalculateField_management(in_table=polygons_file, field=temp_id, expression="!FID!",
                                    expression_type="PYTHON_9.3", code_block="")
    arcpy.FeatureToPoint_management(polygons_file, points_file)
    log.info("面要素转化为点要素")


def delete_polygon_fields(polygons_file):
    """
    只是在测试阶段用于删除生成的字段
    :param polygons_file: 地块文件
    :return:
    """
    field_list = [
        "S1", "nS1", "S21", "nS21", "S22", "nS22", "S23", "nS23",
        "nS2", "N1", "nN1", "N2", "nN2", "N3", "nN3", "S", "N", "C",
        "S11_", "nS11_", "S12_", "nS12_", "S21_", "nS21_", "S22_", "nS22_",
        "N1_", "nN1_", "N2_", "nN2_", "S_", "N_", "C_", "Risk",
        "XF_N1", "HW_N1", "HW_N2", "Pop", "CA_Per", "B_Area0", "B_Area",
        "Temp1", "Temp2", "E_Area", "F_Area"
    ]
    flds = arcpy.ListFields(polygons_file)

    for fld in flds:
        if fld.name in field_list:
            log.info("删除字段: %s" % fld.name)
            arcpy.DeleteField_management(polygons_file, fld.name)
    log.info("现有指标删除完成！即将进行更新...")


def str_2_list(B_Types):
    """
    将B_Types字段转化为列表
    :param B_Types: 输入B_Types字段
    :return: 建筑类型的列表
    """
    if B_Types == "" or "NAN" in B_Types:
        return []
    elif ", " not in B_Types:
        return [B_Types]
    else:
        return B_Types.split(", ")


if __name__ == '__main__':
    # arcpy.env.overwriteOutput = True
    # polygons_file0 = r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp"
    # pop_raster0 = r"D:\lb\myCode\assessment\data\data_for_test\pop\hubei_pop.tif"
    # output_table0 = r"D:\lb\myCode\assessment\data\temp\pop.dbf"
    #
    # # # select_express0 = r"'N_DLBM'='1310'"
    # # select_express0 = '"N_DLBM"' + "='1310'"
    # # selected_feature0 = r"D:\lb\myCode\assessment\data\temp\fire_station.shp"
    # #
    # # select_feature(polygons_file0, select_express0, selected_feature0)
    #
    # delete_polygon_fields(polygons_file0)

    test_str = "2014新建"
    test_str0 = test_str[0: 4: 1]
    print(test_str0)
