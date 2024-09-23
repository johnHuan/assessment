# coding=utf-8
# @Time : 2024/7/6 9:48
# @Author : Trifurs
# @File : S1.py
# @Software : PyCharm


import os
from tools.accessibility import get_accessibility
from tools.data_manager import field_normalize, add_field
from tools.accessibility_road import compute_time


class S1(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons"]
        self.buffers = data_dict['buffers']["fire_buffers"]
        self.temp_file = data_dict['directories']["temp_file"]
        # self.roads = data_dict["roads"]
        self.polygon_poi = os.path.join(self.temp_file, "polygons_poi.shp")
        self.fire_station = os.path.join(self.temp_file, "fire_station.shp")
        self.fire_station_poi = os.path.join(self.temp_file, "fire_station_poi.shp")

        self.get_S1()

    def get_S1(self):   # 缓冲区方法
        get_accessibility(self.polygons, self.fire_station, self.buffers,
                          self.temp_file, weight_index=500.0, count_name="S1")
        field_normalize(self.polygons, "S1", "nS1")

    # def get_S1(self):   # 路网方法 计算结果存在问题
    #     cut_off = 10.0
    #     od_dict = compute_time(self.temp_file, self.polygon_poi, self.fire_station_poi, self.roads, cut_off)
    #     add_field(self.polygons, "Fire_FID", "SHORT")
    #     add_field(self.polygons, "S1", "DOUBLE")
    #     fc_rows = arcpy.UpdateCursor(self.polygons)
    #     while True:
    #         fc_row = fc_rows.next()
    #         if not fc_row:
    #             break
    #         if fc_row.FID in od_dict.keys():
    #             fc_row.Fire_FID = od_dict[fc_row.FID][0]
    #             fc_row.S1 = cut_off * 1.1 - od_dict[fc_row.FID][1]
    #         else:
    #             fc_row.S1 = cut_off * 1.1
    #         fc_rows.updateRow(fc_row)
    #     del fc_rows
    #
    #     field_normalize(self.polygons, "S1", "nS1")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy
    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
        "temp_file": r"D:\lb\myCode\assessment\data\temp\valuation",  # 临时文件夹
        "buffers": [100.0, 500.0, 1000.0, 2000.0, 5000.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
        "roads": r"D:\lb\myCode\assessment\data\data_for_test\roads\roads_cut_topo_ND.nd"  # 路网数据
    }

    S1(config_dict)
