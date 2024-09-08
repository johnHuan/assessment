# coding=utf-8
# @Time : 2024/7/7 11:07
# @Author : Trifurs
# @File : N1_.py
# @Software : PyCharm


import arcpy
from code.tools.data_manager import add_field, field_normalize


class N1_(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons"]
        self.C = data_dict['parameters']["C"]
        self.A = data_dict['parameters']["A"]

        self.get_N1_()

    def get_N1_(self):
        add_field(self.polygons, "N1_", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="N1_",
                                        expression="!HW_N1! * (!Pop! * " + str(self.C)
                                                   + " * " + str(self.A) + " / 1000.0)",
                                        expression_type="PYTHON_9.3", code_block="")
        field_normalize(self.polygons, "N1_", "nN1_")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy

    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
        "C": "1.1",  # 预测的平均日人均生活垃圾产量[kg/(人·d)]，可取0.8kg/(人·d) ~ 1.4kg/(人·d)
        "A": "1.3"  # 生活垃圾日产量不均匀系数，可取1 ~ 1.5
    }

    N1_(config_dict)
