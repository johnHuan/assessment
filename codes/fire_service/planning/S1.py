# coding=utf-8
# @Time : 2024/7/9 9:35
# @Author : Trifurs
# @File : S1.py
# @Software : PyCharm


import os
from codes.tools.accessibility import get_accessibility
from codes.tools.data_manager import field_normalize


class S1(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons_for_planning"]
        self.buffers = data_dict['buffers']["fire_buffers"]
        self.temp_file = data_dict['directories']["temp_file_planning"]
        self.fire_station = os.path.join(self.temp_file, "fire_station.shp")

        self.get_S1()

    def get_S1(self):
        get_accessibility(self.polygons, self.fire_station, self.buffers,
                          self.temp_file, weight_index=500.0, count_name="S1")
        field_normalize(self.polygons, "S1", "nS1")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy
    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 用于规划的用地数据
        "temp_file_planning": r"D:\lb\myCode\assessment\data\temp\planning",  # 临时文件夹
        "buffers": [100.0, 500.0, 1000.0, 2000.0, 5000.0]  # 计算可达性的多级缓冲区的缓冲半径（米）
    }

    S1(config_dict)
