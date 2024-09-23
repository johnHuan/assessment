# coding=utf-8
# @Time : 2024/7/9 14:48
# @Author : Trifurs
# @File : N1.py
# @Software : PyCharm


import os
import arcpy
from tools.data_manager import add_field, field_normalize


class N1(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons_for_planning"]

        self.get_N1()

    def get_N1(self):
        add_field(self.polygons, "N1", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="N1",
                                        expression="(!Pop! / !Area!) * !XF_N1!",
                                        expression_type="PYTHON_9.3", code_block="")
        field_normalize(self.polygons, "N1", "nN1")

    def __iter__(self):
        pass


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 地块数据
    }

    N1(config_dict)
