# coding=utf-8
# @Time : 2024/7/8 8:56
# @Author : Trifurs
# @File : sanitation_valuation.py
# @Software : PyCharm


import arcpy
import gc
from S1_ import S1_
from S2_ import S2_
from N1_ import N1_
from N2_ import N2_
from code.tools.data_manager import add_field


class Sanitation_SNC(object):
    """环卫服务供给S、需求N、匹配度C"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        print("\n正在评估环卫服务能力...")

        S2_(data_dict)
        # del S2_
        gc.collect()
        print("\nS2_计算完成！")

        S1_(data_dict)
        # del S1_
        gc.collect()
        print("\nS1_计算完成！")

        N1_(data_dict)
        # del N1_
        gc.collect()
        print("\nN1_计算完成！")

        N2_(data_dict)
        # del N2_
        gc.collect()
        print("\nN2_计算完成！\n")

        self.polygons = data_dict['shp_path']["polygons"]

        self.get_S_()
        self.get_N_()
        self.get_C_()

        print("环卫服务能力评估完成！\n")

    def get_S_(self):
        add_field(self.polygons, "S_", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="S_",
                                        expression="!nS11_! * 0.20833 + !nS12_! * 0.38542 + "
                                                   "!nS21_! * 0.16667 + !nS22_! * 0.23958",
                                        expression_type="PYTHON_9.3", code_block="")

    def get_N_(self):
        add_field(self.polygons, "N_", "DOUBLE")
        arcpy.CalculateField_management(in_table=self.polygons, field="N_",
                                        expression="!nN1_! * 0.625 + !nN2_! * 0.375",
                                        expression_type="PYTHON_9.3", code_block="")

    def get_C_(self):
        add_field(self.polygons, "C_", "DOUBLE")

        C__list = []
        fc_rows = arcpy.SearchCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.N_ != 0:
                C__list.append(fc_row.S_ / fc_row.N_)
        del fc_rows

        fc_rows = arcpy.UpdateCursor(self.polygons)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.N_ != 0:
                fc_row.C_ = fc_row.S_ / fc_row.N_
            else:
                fc_row.C_ = max(C__list) * 1.1  # 需求量为0的地块匹配度取最大值的1.1倍
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
        "buildings_dir": r"D:\lb\myCode\assessment\data\data_for_test\buildings",  # 建筑数据所在目录
        "C": "1.1",  # 预测的平均日人均生活垃圾产量[kg/(人·d)]，可取0.8kg/(人·d) ~ 1.4kg/(人·d)
        "A": "1.3"  # 生活垃圾日产量不均匀系数，可取1 ~ 1.5
    }

    Sanitation_SNC(config_dict)
