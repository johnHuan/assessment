# coding=utf-8
# @Time : 2024/7/6 17:31
# @Author : Trifurs
# @File : fire_valuation.py
# @Software : PyCharm


import arcpy
from S1 import S1
from S2 import S2
from N1 import N1
from N2 import N2
from N3 import N3
from code_s.tools.data_manager import add_field


class Fire_SNC(object):
    """消防服务供给S、需求N、匹配度C"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        print("\n正在评估消防服务能力...")

        self.polygons = data_dict["polygons"]

        S1(data_dict)
        S2(data_dict)
        N1(data_dict)
        N2(data_dict)
        N3(data_dict)

        self.get_S()
        self.get_N()
        self.get_C()

        print("消防服务能力评估完成！\n")

    def get_S(self):
        add_field(self.polygons, "S", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="S",
                                        expression="!nS1! * 0.625 + !nS2! * 0.375",
                                        expression_type="PYTHON_9.3", code_block="")

    def get_N(self):
        add_field(self.polygons, "N", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="N",
                                        expression="!nN1! * 0.41667 + !nN2! * 0.41667 + !nN3! * 0.16667",
                                        expression_type="PYTHON_9.3", code_block="")

    def get_C(self):
        add_field(self.polygons, "C", "DOUBLE")
        C_list = []
        fc_rows = arcpy.SearchCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.N != 0:
                C_list.append(fc_row.S / fc_row.N)
        del fc_rows

        fc_rows = arcpy.UpdateCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.N != 0:
                fc_row.C = fc_row.S / fc_row.N
            else:
                fc_row.C = max(C_list) * 1.1  # 需求量为0的地块匹配度取最大值的1.1倍
            fc_rows.updateRow(fc_row)
        del fc_rows

    def __iter__(self):
        pass


if __name__ == '__main__':
    import arcpy

    arcpy.env.overwriteOutput = True
    config_dict = {
        "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
        "temp_file": r"D:\lb\myCode\assessment\data\temp\valuation",  # 临时文件夹
        "buffers": [100.0, 500.0, 1000.0, 2000.0, 5000.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
        "hazard_buffers": [10.0, 50.0, 100.0, 200.0, 500.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
        "hazardous_facilities": r"D:\lb\myCode\assessment\data\data_for_test\POIs\hazardous_facilities.shp",  # 危险设施POI
        "buildings_dir": r"D:\lb\myCode\assessment\data\data_for_test\buildings",  # 建筑数据所在目录
        "pop_raster": r"D:\lb\myCode\assessment\data\data_for_test\pop\hubei_pop.tif",  # 人口密度栅格
    }

    Fire_SNC(config_dict)
