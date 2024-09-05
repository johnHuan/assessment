# coding=utf-8
# @Time : 2024/7/9 15:57
# @Author : Trifurs
# @File : N2_.py
# @Software : PyCharm


import arcpy
from code_s.tools.data_manager import add_field, field_normalize


class N2_(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons_for_planning"]
        self.C = data_dict['parameters']["C"]
        self.A = data_dict['parameters']["A"]

        self.get_N2_()

    def get_N2_(self):
        add_field(self.polygons, "N2_", "DOUBLE")
        fc_rows = arcpy.UpdateCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            # print(str(fc_row.CA_Per))
            if str(fc_row.CA_Per) == "nan":
                # print(str(fc_row.CA_Per))
                fc_row.N2_ = 0
            else:
                fc_row.N2_ = (fc_row.Area * fc_row.FAR / fc_row.CA_Per) * self.C * self.A
            fc_rows.updateRow(fc_row)
        del fc_rows

        field_normalize(self.polygons, "N2_", "nN2_")

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy

    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 地块数据
        "C": "1.1",  # 预测的平均日人均生活垃圾产量[kg/(人·d)]，可取0.8kg/(人·d) ~ 1.4kg/(人·d)
        "A": "1.3"  # 生活垃圾日产量不均匀系数，可取1 ~ 1.5
    }

    N2_(config_dict)
