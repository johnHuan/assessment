# coding=utf-8
# @Time : 2024/7/6 17:20
# @Author : Trifurs
# @File : N3.py
# @Software : PyCharm


from code_s.tools.accessibility import get_accessibility
from code_s.tools.data_manager import field_normalize


class N3(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.hazardous_facilities = data_dict["hazardous_facilities"]
        self.hazard_buffers = data_dict["hazard_buffers"]
        self.polygons = data_dict["polygons"]
        self.temp_file = data_dict["temp_file"]

        self.get_N3()

    def get_N3(self):
        get_accessibility(self.polygons, self.hazardous_facilities,
                          self.hazard_buffers, self.temp_file, count_name="N3")
        field_normalize(self.polygons, "N3", "nN3")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy
    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
        "temp_file": r"D:\lb\myCode\assessment\data\temp",  # 临时文件夹
        "hazard_buffers": [10.0, 50.0, 100.0, 200.0, 500.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
        "hazardous_facilities": r"D:\lb\myCode\assessment\data\data_for_test\POIs\hazardous_facilities.shp"  # 危险设施POI
    }

    N3(config_dict)

