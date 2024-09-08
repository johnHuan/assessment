# coding=utf-8
# @Time : 2024/7/9 14:58
# @Author : Trifurs
# @File : N2.py
# @Software : PyCharm


import arcpy
from code.tools.data_manager import add_field, field_normalize


class N2(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.fire_station = ""
        self.polygons = data_dict['shp_path']["polygons_for_planning"]

        self.get_N2()

    def get_N2(self):
        add_field(self.polygons, "N2", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="N2",
                                        expression="!Area! * !FAR! * !Risk!",
                                        expression_type="PYTHON_9.3", code_block="")
        field_normalize(self.polygons, "N2", "nN2")

    def __iter__(self):
        pass


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 地块数据
    }

    N2(config_dict)
