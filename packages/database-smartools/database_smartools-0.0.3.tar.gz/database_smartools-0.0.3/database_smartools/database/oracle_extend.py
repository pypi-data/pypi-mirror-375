# -*- coding: utf-8 -*-

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