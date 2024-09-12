# coding=utf-8
# @Time : 2024/7/7 8:41
# @Author : Trifurs
# @File : S1_.py
# @Software : PyCharm


import os
import arcpy
from codes.tools.accessibility import get_accessibility
from codes.tools.data_manager import add_field, field_normalize, polygon2point


class S1_(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons"]
        self.buffers = data_dict['buffers']["collection_buffers"]
        self.temp_file = data_dict['directories']["temp_file"]
        self.collection_station = os.path.join(self.temp_file, "garbage_collection_station.shp")
        self.collection_station_poi = os.path.join(self.temp_file, "garbage_collection_station_poi.shp")

        self.get_S11_()
        self.get_S12_()

    def get_S11_(self):
        get_accessibility(self.polygons, self.collection_station, self.buffers,
                          self.temp_file, weight_index=500.0, count_name="S11_")
        field_normalize(self.polygons, "S11_", "nS11_")

    def get_S12_(self):
        polygon2point(self.collection_station, self.collection_station_poi)
        thiessen_shp = os.path.join(self.temp_file, "c_thiessen.shp")  # 垃圾收集站构建的泰森多边形
        polygons_poi = os.path.join(self.temp_file, "polygons_poi.shp")  # 地块转点（在消防评估中已完成）
        intersect_file = os.path.join(self.temp_file, "cp_intersects.shp")
        arcpy.env.extent = self.polygons
        arcpy.CreateThiessenPolygons_analysis(self.collection_station_poi, thiessen_shp, "ALL")

        arcpy.Intersect_analysis([polygons_poi, thiessen_shp], intersect_file, "ALL", "", "")
        collection_dict = {}  # 垃圾收集站id、建筑面积
        fc_rows = arcpy.SearchCursor(intersect_file)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            collection_dict[fc_row.Temp1] = fc_row.JU_Area
        del fc_rows

        # print(collection_dict)

        add_field(self.polygons, "S12_", "DOUBLE")
        fc_rows = arcpy.UpdateCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            fc_row.S12_ = collection_dict[fc_row.Temp1]
            fc_rows.updateRow(fc_row)
        del fc_rows

        field_normalize(self.polygons, "S12_", "nS12_")

        # arcpy.DeleteField_management(self.polygons, "Temp1")
        # arcpy.DeleteField_management(self.polygons, "Temp2")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy

    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
        "temp_file": r"D:\lb\myCode\assessment\data\temp",  # 临时文件夹
        "buffers": [100.0, 500.0, 1000.0, 2000.0, 5000.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
    }

    S1_(config_dict)
