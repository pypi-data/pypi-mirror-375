# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : oracle_extend.py
@创建人   : zhongbinjie
@创建时间 : 2025/7/2 16:14
@文件说明 :
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""
import dmPython
from datetime import date, datetime, timedelta
from decimal import Decimal


def formatter(result):
    data = []
    for row in result["data"]:
        item_map = {}
        for index, item in enumerate(row):
            column_type = result["desc"][index][1]
            if item is not None:
                if column_type == dmPython.BOOLEAN:
                    # 将达梦 BOOLEAN 类型转换为 Python bool 类型
                    item = bool(item)
                elif column_type == dmPython.BINARY:
                    # 将达梦 BINARY 类型转换为 Python bytes 类型
                    item = bytes(item)
                elif column_type == dmPython.DATE:
                    # 将达梦 DATE 类型转换为 Python datetime.date 类型
                    item = datetime(item.year, item.month, item.day)
                elif column_type == dmPython.TIMESTAMP:
                    # 将达梦 TIMESTAMP 类型转换为 Python datetime.datetime 类型
                    item = datetime(
                        item.year,
                        item.month,
                        item.day,
                        item.hour,
                        item.minute,
                        item.second,
                        item.microsecond,
                    )
                elif column_type == dmPython.INTERVAL:
                    # 将达梦 INTERVAL 类型转换为 Python datetime.timedelta 类型
                    item = timedelta(
                        days=item.days,
                        seconds=item.seconds,
                        microseconds=item.microseconds,
                    )
                elif column_type == dmPython.DECIMAL:
                    # 将达梦 DECIMAL 类型转换为 Python decimal.Decimal 类型
                    item = float(item)
                elif column_type == dmPython.REAL:
                    # 将达梦 REAL 类型转换为 Python float 类型
                    item = float(item)
                elif column_type == dmPython.BIGINT:
                    # 将达梦 BIGINT 类型转换为 Python int 类型
                    item = int(item)
                elif column_type == dmPython.STRING:
                    # 将达梦 STRING 类型转换为 Python str 类型
                    item = str(item)

            item_map[result["desc"][index][0].lower()] = item
        data.append(item_map)
    return data
