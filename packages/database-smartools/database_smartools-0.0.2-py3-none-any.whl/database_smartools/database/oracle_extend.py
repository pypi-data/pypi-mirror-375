# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : oracle_extend.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

import oracledb
def formatter(result):
    data = []
    for row in result['data']:
        item_map = {}
        for index, item in enumerate(row):
            # if result['desc'][index][1] == cx_Oracle.DATETIME and item is not None:
            # 	item = item.strftime("%Y-%m-%d")

            if result['desc'][index][1] == oracledb.TIMESTAMP and item is not None:
                item = item.strftime("%Y-%m-%d %H:%M:%S")

            item_map[result['desc'][index][0].lower()] = item

        data.append(item_map)
    return data