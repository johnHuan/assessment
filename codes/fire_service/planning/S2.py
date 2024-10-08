# coding=utf-8
# @Time : 2024/7/9 9:53
# @Author : Trifurs
# @File : S2.py
# @Software : PyCharm


import os
import arcpy
from codes.tools.data_manager import polygon2point, add_field, field_normalize, get_fire_station_level
import sys

reload(sys)
sys.setdefaultencoding('utf8')


class S2(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.fire_station = ""
        self.polygons = data_dict['shp_path']["polygons_for_planning"]
        self.temp_file = data_dict['directories']["temp_file_planning"]
        self.fire_station = os.path.join(self.temp_file, "fire_station.shp")
        self.fire_station_poi = os.path.join(self.temp_file, "fire_station_poi.shp")

        self.fire_station_allocate()
        self.get_S2()

    def fire_station_allocate(self):
        polygon2point(self.fire_station, self.fire_station_poi)
        thiessen_shp = os.path.join(self.temp_file, "f_thiessen.shp")  # 消防站构建的泰森多边形
        polygons_poi = os.path.join(self.temp_file, "polygons_poi.shp")  # 地块转点 环卫评估已计算
        intersect_file = os.path.join(self.temp_file, "fp_intersects.shp")
        arcpy.env.extent = self.polygons
        arcpy.CreateThiessenPolygons_analysis(self.fire_station_poi, thiessen_shp, "ALL")

        arcpy.Intersect_analysis([polygons_poi, thiessen_shp], intersect_file, "ALL", "", "")
        fire_dict = {}  # 消防站id、等级、消防员数量、设备数量
        fc_rows = arcpy.SearchCursor(intersect_file)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.Sta_Type_1 == 0:  # 该字段为0表示外围现有的消防用地
                fire_dict[fc_row.Temp1] = [fc_row.Shape_Area, fc_row.B_Area, fc_row.B_Area0]
            else:
                fire_dict[fc_row.Temp1] = [
                    fc_row.Area_1, fc_row.Area_1 * fc_row.FAR_1, fc_row.Area_1 * fc_row.BD_1
                ]
        del fc_rows

        add_field(self.polygons, "S21", "DOUBLE")
        add_field(self.polygons, "S22", "DOUBLE")
        add_field(self.polygons, "S23", "DOUBLE")
        fc_rows = arcpy.UpdateCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            fc_row.S21 = fire_dict[fc_row.Temp1][0]
            fc_row.S22 = fire_dict[fc_row.Temp1][1]
            fc_row.S23 = fire_dict[fc_row.Temp1][2]
            fc_rows.updateRow(fc_row)
        del fc_rows

        field_normalize(self.polygons, "S21", "nS21")
        field_normalize(self.polygons, "S22", "nS22")
        field_normalize(self.polygons, "S23", "nS23")

    def get_S2(self):
        add_field(self.polygons, "nS2", "DOUBLE")  # 由3个标准化的下级指标计算得到的结果不用再标准化
        arcpy.CalculateField_management(in_table=self.polygons, field="nS2",
                                        expression="!nS21! * 0.24383 + !nS22! * 0.36201 + !nS23! * 0.39415",
                                        expression_type="PYTHON_9.3", code_block="")

    def __iter__(self):
        pass


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 地块数据
        "temp_file_planning": r"D:\lb\myCode\assessment\data\temp\planning",  # 临时文件夹
    }

    S2(config_dict)
