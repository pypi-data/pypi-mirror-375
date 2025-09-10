# -*- coding: utf-8 -*-

import jaydebeapi

def formatter(result):
    data = []
    if not result or not result['data']:
        return data
    for index, row in enumerate(result['data']):
        item_map = {}
        for index, item in enumerate(row):
            #
            # if result['desc'][index][1] == jaydebeapi.DATETIME and item is not None:
            #      item = texter.convert_to_oracle_datetime(item, 'TIMESTAMP')
            #
            # if result['desc'][index][1] == jaydebeapi.DATE and item is not None:
            #      item = texter.convert_to_oracle_datetime(item, 'DATE')

            # if result['desc'][index][1] not in ['VARCHAR2', 'DATE']:
            #     print(result['desc'][index][1])
            item_map[result['desc'][index][0].lower()] = item
        data.append(item_map)

    return data

def test_connect_oceanbase(url, user, password, driver, jarFile):
    """
    测试连接 OceanBase 数据库
    :param url: 数据库连接字符串
    :param user: 用户名
    :param password: 密码
    :param driver: 驱动类名
    :param jarFile: 驱动 JAR 文件路径
    :return:
    """
    sqlStr = """select 1 from dual"""
    conn = jaydebeapi.connect(driver, url, [user, password], jarFile)
    return conn


def test():
    print()


if __name__ == '__main__':
    # sqlStr = "SELECT * FROM user_tab_columns WHERE table_name = 'T_CHECK_LOG_TEST'"
    None
