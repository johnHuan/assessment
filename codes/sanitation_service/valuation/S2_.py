# coding=utf-8
# @Time : 2024/7/7 10:55
# @Author : Trifurs
# @File : S2_.py
# @Software : PyCharm


import os
import arcpy
from codes.tools.accessibility import get_accessibility
from codes.tools.data_manager import add_field, field_normalize, polygon2point


class S2_(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons"]
        self.buffers = data_dict['buffers']["transfer_buffers"]
        self.temp_file = data_dict['directories']["temp_file"]
        self.transfer_station = os.path.join(self.temp_file, "garbage_transfer_station.shp")
        self.transfer_station_poi = os.path.join(self.temp_file, "garbage_transfer_station_poi.shp")

        self.get_S21_()
        self.get_S22_()

    def get_S21_(self):
        get_accessibility(self.polygons, self.transfer_station, self.buffers,
                          self.temp_file, weight_index=2000.0, count_name="S21_")
        field_normalize(self.polygons, "S21_", "nS21_")

    def get_S22_(self):
        polygon2point(self.transfer_station, self.transfer_station_poi)
        thiessen_shp = os.path.join(self.temp_file, "t_thiessen.shp")  # 垃圾转运站构建的泰森多边形
        polygons_poi = os.path.join(self.temp_file, "polygons_poi.shp")  # 地块转点
        intersect_file = os.path.join(self.temp_file, "tp_intersects.shp")
        polygon2point(self.polygons, polygons_poi)
        arcpy.env.extent = self.polygons
        arcpy.CreateThiessenPolygons_analysis(self.transfer_station_poi, thiessen_shp, "ALL")

        arcpy.Intersect_analysis([polygons_poi, thiessen_shp], intersect_file, "ALL", "", "")
        transfer_dict = {}  # 垃圾转运站id、建筑面积
        fc_rows = arcpy.SearchCursor(intersect_file)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            transfer_dict[fc_row.Temp1] = fc_row.JU_Area
        del fc_rows

        # print(transfer_dict)

        add_field(self.polygons, "S22_", "DOUBLE")
        fc_rows = arcpy.UpdateCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            fc_row.S22_ = transfer_dict[fc_row.Temp1]
            fc_rows.updateRow(fc_row)
        del fc_rows

        field_normalize(self.polygons, "S22_", "nS22_")

        # arcpy.DeleteField_management(self.polygons, "Temp1")
        # arcpy.DeleteField_management(self.polygons, "Temp2")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy

    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons": r"C:\Users\Administrator\Desktop\assessment\data\data_sources\polygons\polygons.shp",  # 地块数据
        "temp_file": r"C:\Users\Administrator\Desktop\assessment\data\temp\valuation",  # 临时文件夹
        "transfer_buffers": [2000.0, 4000.0, 6000.0, 8000.0, 10000.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
    }

    S2_(config_dict)

