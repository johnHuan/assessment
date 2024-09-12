# coding=utf-8
# @Time : 2024/7/6 9:27
# @Author : Trifurs
# @File : data_prepare.py
# @Software : PyCharm


import arcpy
import os
import time
import pandas as pd
from dbfread import DBF
from file_helper import get_fire_risk, get_per_area, get_n_extent
from accessibility import feature_buffer
from data_manager import add_field, polygon2point, select_feature_by_attribution
from data_manager import delete_polygon_fields, str_2_list, select_feature_by_location
from data_manager import get_year_risk
import sys
import yaml

from codes.logging_ import logging_

with open('./configs.yaml', 'r') as f_y:
    content = f_y.read()
configs = yaml.safe_load(content)
_path = configs['log_path']
log = logging_(_path).logger  # 实例化封装类


reload(sys)
sys.setdefaultencoding('utf8')


class Valuation_Preparation(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons_file = data_dict['shp_path']["polygons"]
        self.temp_file = data_dict['directories']["temp_file"]
        self.pop_raster = data_dict['other_files']["pop_raster"]
        self.buildings_dir = data_dict['directories']["buildings_dir"]
        self.fire_risk_weights = data_dict['excel_path']["fire_risk_weights"]
        self.per_CA = data_dict['excel_path']["per_capita_service_area"]
        self.n_extent = data_dict['excel_path']["N_extent"]
        self.buildings_shp = os.path.join(self.temp_file, "buildings.shp")
        self.building_points = os.path.join(self.temp_file, "building_points.shp")
        self.fire_station = os.path.join(self.temp_file, "fire_station.shp")
        self.collection_station = os.path.join(self.temp_file, "garbage_collection_station.shp")
        self.transfer_station = os.path.join(self.temp_file, "garbage_transfer_station.shp")

        self.polygon_buildings_dict = {}
        delete_polygon_fields(self.polygons_file)

        self.read_tables()
        self.count_polygon_pop()
        self.merge_buildings()
        self.get_building_areas()
        self.link_areas_2_polygon()
        self.get_fire_station()
        self.get_garbage_station()
        self.compute_effective_area()

    def read_tables(self):
        get_fire_risk(self.fire_risk_weights, self.polygons_file)
        get_per_area(self.per_CA, self.polygons_file)
        get_n_extent(self.n_extent, self.polygons_file)

    def count_polygon_pop(self):
        output_table = os.path.join(self.temp_file, "pop.dbf")
        arcpy.gp.ZonalStatisticsAsTable_sa(self.polygons_file,
                                           "OBJECTID", self.pop_raster,
                                           output_table, "DATA", "SUM")
        table = DBF(output_table, encoding='utf-8')
        df = pd.DataFrame(iter(table))
        id_pop_dict = {}
        for row in range(df.shape[0]):
            id_pop_dict[df["OBJECTID"][row]] = df["SUM"][row]

        add_field(self.polygons_file, "Pop", 'DOUBLE')

        fc_rows = arcpy.UpdateCursor(self.polygons_file)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.OBJECTID in id_pop_dict.keys():
                fc_row.Pop = id_pop_dict[fc_row.OBJECTID]
            else:
                fc_row.Pop = 0
            fc_rows.updateRow(fc_row)
        del fc_rows

    def merge_buildings(self):
        input_file = []
        for shp in os.listdir(self.buildings_dir):
            if shp.endswith(".shp"):
                building_shp = os.path.join(self.buildings_dir, shp)
                input_file.append(building_shp)  # 循环加入所有shape文件
                # print(shp)
                add_field(building_shp, "B_Type", "TEXT")
                add_field(building_shp, "b_area", "DOUBLE")
                compute_expression = '"' + shp.split(".")[0] + '"'
                arcpy.CalculateField_management(in_table=building_shp, field="B_Type",
                                                expression=compute_expression,
                                                expression_type="PYTHON_9.3", code_block="")
                arcpy.CalculateField_management(in_table=building_shp, field="b_area",
                                                expression="!建筑面!",
                                                expression_type="PYTHON_9.3", code_block="")

        # print(input_file)

        arcpy.Merge_management(inputs=input_file,
                               output=self.buildings_shp)  # 输出到ArcGIS默认数据库中

    def get_building_areas(self):
        polygon2point(self.buildings_shp, self.building_points)
        intersect_file = os.path.join(self.temp_file, "bp_intersects.shp")
        arcpy.Intersect_analysis([self.building_points, self.polygons_file],
                                 intersect_file, "ALL", "", "")

        # time.sleep(5)   # 在部分设备上必须休眠一段时间，负责无法生成中间文件
        # add_field(intersect_file, "Temp1", 'DOUBLE')
        add_field(intersect_file, "Temp3", 'TEXT')

        arcpy.CalculateField_management(in_table=intersect_file, field="Temp1", expression="!基底面!",
                                        expression_type="PYTHON_9.3", code_block="")
        arcpy.CalculateField_management(in_table=intersect_file, field="Temp2", expression="!建筑面!",
                                        expression_type="PYTHON_9.3", code_block="")
        arcpy.CalculateField_management(in_table=intersect_file, field="Temp3", expression="!建筑年!",
                                        expression_type="PYTHON_9.3", code_block="")

        # 建筑点 => OBJECTID,    地块 => OBJECTID_1
        polygon_buildings_dict = {}

        fc_rows = arcpy.SearchCursor(intersect_file)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.OBJECTID_1 not in polygon_buildings_dict.keys():
                polygon_buildings_dict[fc_row.OBJECTID_1] = [
                    fc_row.Temp1,
                    fc_row.Temp2,
                    fc_row.Temp2 * get_year_risk(fc_row.Temp3)
                ]
            else:
                temp = polygon_buildings_dict[fc_row.OBJECTID_1]
                polygon_buildings_dict[fc_row.OBJECTID_1] = [
                    temp[0] + fc_row.Temp1,
                    temp[1] + fc_row.Temp2,
                    temp[2] + fc_row.Temp2 * get_year_risk(fc_row.Temp3)
                ]
        del fc_rows

        arcpy.DeleteField_management(intersect_file, "Temp1")
        arcpy.DeleteField_management(intersect_file, "Temp2")
        arcpy.DeleteField_management(intersect_file, "Temp3")

        # print(polygon_buildings_dict)

        self.polygon_buildings_dict = polygon_buildings_dict

    def link_areas_2_polygon(self):
        add_field(self.polygons_file, "B_Area0", 'DOUBLE')
        add_field(self.polygons_file, "B_Area", 'DOUBLE')
        add_field(self.polygons_file, "F_Area", 'DOUBLE')

        fc_rows = arcpy.UpdateCursor(self.polygons_file)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if fc_row.OBJECTID not in self.polygon_buildings_dict.keys():
                fc_row.B_Area0 = 0
                fc_row.B_Area = 0
                fc_row.F_Area = 0
            else:
                fc_row.B_Area0 = self.polygon_buildings_dict[fc_row.OBJECTID][0]
                fc_row.B_Area = self.polygon_buildings_dict[fc_row.OBJECTID][1]
                fc_row.F_Area = self.polygon_buildings_dict[fc_row.OBJECTID][2]
            fc_rows.updateRow(fc_row)
        del fc_rows

    def compute_effective_area(self):
        # 建筑点与用地数据相交 get_building_areas函数已计算
        bp_intersects = os.path.join(self.temp_file, "bp_intersects.shp")
        effective_area_dict = {}
        fc_rows = arcpy.SearchCursor(bp_intersects)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            type_list = str_2_list(fc_row.B_Types)
            if fc_row.OBJECTID_1 not in effective_area_dict.keys():
                if fc_row.CA_Per is None or len(type_list) == 0 or fc_row.B_Type not in type_list:
                    effective_area_dict[fc_row.OBJECTID_1] = 0
                else:
                    effective_area_dict[fc_row.OBJECTID_1] = fc_row.b_area
            else:
                if fc_row.CA_Per is None or len(type_list) == 0 or fc_row.B_Type not in type_list:
                    effective_area_dict[fc_row.OBJECTID_1] += 0
                else:
                    effective_area_dict[fc_row.OBJECTID_1] += fc_row.b_area
        del fc_rows

        add_field(self.polygons_file, "E_Area", "DOUBLE")
        fc_rows1 = arcpy.UpdateCursor(self.polygons_file)
        while True:
            fc_row1 = fc_rows1.next()
            if not fc_row1:
                break
            if fc_row1.OBJECTID in effective_area_dict.keys():
                fc_row1.E_Area = effective_area_dict[fc_row1.OBJECTID]
            else:
                fc_row1.E_Area = 0
            fc_rows1.updateRow(fc_row1)
        del fc_rows1

    def get_fire_station(self):
        # select_express = r"'N_DLBM'='1310'"   # 实验表明这个SQL语句会出错
        select_express = '"N_DLBM"' + "='1310'"
        select_feature_by_attribution(self.polygons_file, select_express, self.fire_station)

    def get_garbage_station(self):
        JU_buildings = os.path.join(self.buildings_dir, "JU.shp")
        add_field(JU_buildings, "JU_Type", "TEXT")
        add_field(JU_buildings, "JU_Name", "TEXT")
        add_field(JU_buildings, "JU_Area", "DOUBLE")
        arcpy.CalculateField_management(in_table=JU_buildings, field="JU_Name",
                                        expression="!建筑名!",
                                        expression_type="PYTHON_9.3", code_block="")
        arcpy.CalculateField_management(in_table=JU_buildings, field="JU_Area", expression="!建筑面!",
                                        expression_type="PYTHON_9.3", code_block="")

        fc_rows = arcpy.UpdateCursor(JU_buildings)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            # print(fc_row.JU_Name)
            if "垃圾" in fc_row.JU_Name and "转" not in fc_row.JU_Name:
                fc_row.JU_Type = "垃圾收集站"
            elif "转" in fc_row.JU_Name:
                fc_row.JU_Type = "垃圾转运站"
            else:
                pass

            fc_rows.updateRow(fc_row)
        del fc_rows

        select_collection = '"JU_Type"=' + "'垃圾收集站'"
        select_transfer = '"JU_Type"=' + "'垃圾转运站'"

        select_feature_by_attribution(JU_buildings, select_collection, self.collection_station)
        select_feature_by_attribution(JU_buildings, select_transfer, self.transfer_station)

    def __iter__(self):
        pass


class Planning_Preparation(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, data_dict):
        self.polygons_for_planning = data_dict['shp_path']["polygons_for_planning"]
        self.polygons_file = data_dict['shp_path']["polygons"]
        self.temp_file = data_dict['directories']["temp_file"]
        self.temp_file_planning = data_dict['directories']["temp_file_planning"]
        self.buffers = data_dict['buffers']["transfer_buffers"]
        self.hazard_buffers = data_dict['buffers']["hazard_buffers"]
        self.hazardous_facilities = data_dict['shp_path']["hazardous_facilities"]
        self.fire_risk_weights = data_dict['excel_path']["fire_risk_weights"]
        self.per_CA = data_dict['excel_path']["per_capita_service_area"]
        self.n_extent = data_dict['excel_path']["N_extent"]

        self.new_fire_station = os.path.join(self.temp_file_planning, "new_fire_station.shp")
        self.new_collection_station = os.path.join(self.temp_file_planning, "new_collection_station.shp")
        self.new_transfer_station = os.path.join(self.temp_file_planning, "new_transfer_station.shp")

        self.near_fire_stations = os.path.join(self.temp_file_planning, "near_fire_stations.shp")
        self.near_collection_stations = os.path.join(self.temp_file_planning, "near_collection_stations.shp")
        self.near_transfer_stations = os.path.join(self.temp_file_planning, "near_transfer_stations.shp")
        self.near_hazardous_facilities = os.path.join(self.temp_file_planning, "near_hazardous_facilities.shp")

        self.fire_station = os.path.join(self.temp_file_planning, "fire_station.shp")
        self.collection_station = os.path.join(self.temp_file_planning, "garbage_collection_station.shp")
        self.transfer_station = os.path.join(self.temp_file_planning, "garbage_transfer_station.shp")

        delete_polygon_fields(self.polygons_for_planning)
        self.read_tables()
        self.get_station()

    def read_tables(self):
        get_fire_risk(self.fire_risk_weights, self.polygons_for_planning)
        get_per_area(self.per_CA, self.polygons_for_planning)
        get_n_extent(self.n_extent, self.polygons_for_planning)

    def get_new_station(self):
        """将规划样地中可能存在的消防用地、环卫用地加入要素集"""
        add_field(self.polygons_for_planning, "Sta_Type", "SHORT")  # 判断是否为消防/环卫用地
        log.info("开始将规划样地中可能存在的消防用地、环卫用地加入要素集！")
        fc_rows = arcpy.UpdateCursor(self.polygons_for_planning)
        while True:
            fc_row = fc_rows.next()
            if not fc_row:
                break
            if int(fc_row.N_DLBM) == 1310:
                fc_row.Sta_Type = 3  # 消防用地标记为3
            elif int(fc_row.N_DLBM) == 1309:
                if fc_row.JU_Type == "垃圾收集站":
                    fc_row.Sta_Type = 2  # 垃圾收集站标记为2
                elif fc_row.JU_Type == "垃圾转运站":
                    fc_row.Sta_Type = 1  # 垃圾转运站标记为1
                else:
                    fc_row.Sta_Type = 0
            else:
                fc_row.Sta_Type = 0
            fc_rows.updateRow(fc_row)
        del fc_rows

        select_fire = '"Sta_Type"=3'
        select_collection = '"Sta_Type"=2'
        select_transfer = '"Sta_Type"=1'

        select_feature_by_attribution(self.polygons_for_planning, select_fire, self.new_fire_station)
        select_feature_by_attribution(self.polygons_for_planning, select_collection, self.new_collection_station)
        select_feature_by_attribution(self.polygons_for_planning, select_transfer, self.new_transfer_station)
        log.info("将规划样地中可能存在的消防用地、环卫用地加入要素集 完成！")

    def get_near_station(self):
        # 规划样地临近缓冲区
        planning_buffer = os.path.join(self.temp_file_planning, "planning_buffer.shp")
        # 规划样地临近缓冲区（不包含样地自身）
        planning_buffer_without_self = os.path.join(self.temp_file_planning, "planning_buffer_without_self.shp")

        distance = max(self.buffers)
        feature_buffer(self.polygons_for_planning, planning_buffer, distance)
        arcpy.SymDiff_analysis(planning_buffer, self.polygons_for_planning, planning_buffer_without_self, "ALL", "")

        # 消防站
        fire_station = os.path.join(self.temp_file, "fire_station.shp")
        select_feature_by_location(fire_station, planning_buffer_without_self, self.near_fire_stations)

        # 垃圾收集站
        collection_station = os.path.join(self.temp_file, "garbage_collection_station.shp")
        select_feature_by_location(collection_station, planning_buffer_without_self, self.near_collection_stations)

        # 垃圾转运站
        transfer_station = os.path.join(self.temp_file, "garbage_transfer_station.shp")
        select_feature_by_location(transfer_station, planning_buffer_without_self, self.near_transfer_stations)

        # 危险设施
        distance = max(self.hazard_buffers)  # 危险设施计算时缓冲区与消防站、垃圾站不同
        feature_buffer(self.polygons_for_planning, planning_buffer, distance)
        select_feature_by_location(self.hazardous_facilities, planning_buffer, self.near_hazardous_facilities)

    def get_station(self):
        self.get_new_station()
        self.get_near_station()
        arcpy.Merge_management(inputs=[self.near_fire_stations, self.new_fire_station],
                               output=self.fire_station)
        arcpy.Merge_management(inputs=[self.near_collection_stations, self.new_collection_station],
                               output=self.collection_station)
        arcpy.Merge_management(inputs=[self.near_transfer_stations, self.new_transfer_station],
                               output=self.transfer_station)

    def __iter__(self):
        pass


if __name__ == '__main__':
    arcpy.env.overwriteOutput = True
    # config_dict = {
    #     "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
    #     "temp_file": r"D:\lb\myCode\assessment\data\temp\valuation",  # 临时文件夹
    #     "buildings_dir": r"D:\lb\myCode\assessment\data\data_for_test\buildings",  # 建筑数据所在目录
    #     "pop_raster": r"D:\lb\myCode\assessment\data\data_for_test\pop\hubei_pop.tif",  # 人口密度栅格
    #     "fire_risk_weights": r"D:\lb\myCode\assessment\data\data_for_test\tables\fire_risk_weights.xlsx",  # 用地消防风险系数表
    #     "per_capita_service_area": r"D:\lb\myCode\assessment\data\data_for_test\tables\per_capita_service_area.xlsx",  # 人均服务面积表
    #     "N_extent": r"D:\lb\myCode\assessment\data\data_for_test\tables\N_extent.xlsx"  # N计算范围
    # }
    #
    # Valuation_Preparation(config_dict)

    #######################################
    # config_dict = {
    #     "polygons": r"D:\lb\myCode\assessment\data\data_for_test\polygons\test.shp",  # 地块数据
    #     "temp_file_planning": r"D:\lb\myCode\assessment\data\temp\planning",  # 临时文件夹
    #     "temp_file": r"D:\lb\myCode\assessment\data\temp\valuation",  # 临时文件夹
    #     "polygons_for_planning": r"D:\lb\myCode\assessment\data\data_for_test\polygons\planning.shp",  # 用于规划的用地数据
    #     "buffers": [100.0, 500.0, 1000.0, 2000.0, 5000.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
    #     "hazard_buffers": [10.0, 50.0, 100.0, 200.0, 500.0],  # 计算可达性的多级缓冲区的缓冲半径（米）
    #     "hazardous_facilities": r"D:\lb\myCode\assessment\data\data_for_test\POIs\hazardous_facilities.shp",  # 危险设施POI
    #     "fire_risk_weights": r"D:\lb\myCode\assessment\data\data_for_test\tables\fire_risk_weights.xlsx",  # 用地消防风险系数表
    #     "per_capita_service_area": r"D:\lb\myCode\assessment\data\data_for_test\tables\per_capita_service_area.xlsx",
    #     # 人均服务面积表
    #     "N_extent": r"D:\lb\myCode\assessment\data\data_for_test\tables\N_extent.xlsx"  # N计算范围
    # }
    #
    # Planning_Preparation(config_dict)

    building_points0 = r"C:\Users\Administrator\Desktop\assessment\data\temp\valuation\building_points.shp"
    polygons_file0 = r"C:\Users\Administrator\Desktop\assessment\data\data_sources\polygons\polygons.shp"
    intersect_file0 = r"C:\Users\Administrator\Desktop\assessment\data\temp\valuation\bp_intersects.shp"

    arcpy.Intersect_analysis([building_points0, polygons_file0], intersect_file0, "ALL", "", "")
