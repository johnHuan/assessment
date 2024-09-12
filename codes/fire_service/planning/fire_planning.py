# coding=utf-8
# @Time : 2024/7/9 15:20
# @Author : Trifurs
# @File : fire_planning.py
# @Software : PyCharm
import os

import arcpy
import gc

import yaml

from S1 import S1
from S2 import S2
from N1 import N1
from N2 import N2
from N3 import N3
from codes.tools.data_manager import add_field
from codes.logging_ import logging_


class Fire_SNC(object):
    """消防服务供给S、需求N、匹配度C"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons = data_dict['shp_path']["polygons_for_planning"]
        with open('./configs.yaml', 'r') as f_y:
            content = f_y.read()
        configs = yaml.safe_load(content)
        _path = configs['log_path']
        log = logging_(_path).logger  # 实例化封装类
        S1(data_dict)
        # del S1
        gc.collect()
        log.info("S1计算完成！")

        S2(data_dict)
        # del S2
        gc.collect()
        log.info("S2计算完成！")

        N1(data_dict)
        # del N1
        gc.collect()
        log.info("N1计算完成！")

        N2(data_dict)
        # del N2
        gc.collect()
        log.info("N2计算完成！")

        N3(data_dict)
        # del N3
        gc.collect()
        log.info("N3计算完成！")

        self.get_S()
        self.get_N()
        self.get_C()

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
        "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 用于规划的用地数据
        "temp_file_planning": r"D:\lb\myCode\assessment\data\temp\planning",  # 临时文件夹
        "buffers": [100.0, 500.0, 1000.0, 2000.0, 5000.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
        "hazard_buffers": [10.0, 50.0, 100.0, 200.0, 500.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
    }

    Fire_SNC(config_dict)
