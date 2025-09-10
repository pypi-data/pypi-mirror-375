# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : postgre_extend.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

from sqlalchemy import create_engine
import cx_Oracle
from utils import config, logger, texter
import numpy as np

# 获取数据池
cx_Oracle.init_oracle_client(lib_dir=config.MAP['db_lib'])  # 替换为你的Instant Client路径
POOL_MAP = {}


def get_pool():
    pool = cx_Oracle.SessionPool(user=config.MAP['db_user'],
                                 password=config.MAP['db_password'],
                                 dsn=cx_Oracle.makedsn(config.MAP['db_host'], config.MAP['db_port'],
                                                       config.MAP['db_name']),
                                 min=2, max=15, increment=1, threaded=False)
    return pool


def get_pool_by_key(db_key, refresh=False):
    global POOL_MAP
    scan_db_conf = f"""
	SELECT user_name,pass_word,url FROM task_template_data_source WHERE db_key = :db_key
	"""
    params = {"db_key": db_key}
    pool = get_pool()
    conn, message = get_conn(pool)
    select_result, select_message = select(conn, scan_db_conf, params)
    if not select_result:
        return None, select_message
    db_conf = select_result['data'][0]
    user_name = db_conf['user_name']
    pass_word = db_conf['pass_word']
    url = db_conf['url']

    url_map = texter.parse_jdbc_url(url)
    pool = None
    if db_key not in POOL_MAP.keys() or refresh:
        if url_map['type'] == 'oracle':
            try:
                pool = cx_Oracle.SessionPool(user=user_name,
                                             password=pass_word,
                                             dsn=cx_Oracle.makedsn(url_map['host'], url_map['port'],
                                                                   url_map['database']),
                                             min=2, max=15, increment=1, threaded=False)
            except Exception as e:
                message = f"实例化数据库连接池失败，错误信息：{e}"
                logger.error(message)

                return None, message

        POOL_MAP[db_key] = {
            "pool": pool,
            "db_type": url_map['type']
        }
        logger.debug(f"创建新的连接池，db_key: {db_key}")
    else:
        pool = POOL_MAP[db_key][0]
        logger.debug(f"使用已有连接池，db_key: {db_key}")
    return pool, ""


def close_pool(pool):
    pool.close()
    logger.debug(f"关闭连接池")


def get_conn(pool):
    message = ""
    try:
        conn = pool.acquire()
        logger.debug(f"从连接池中获取数据库连接")
        return conn, message
    except Exception as e:
        message = f'获取数据连接异常，错误信息：{e}'
        logger.error(f'获取数据连接异常，错误信息：{e}')
        return None, message


def get_conn_map(pool_map):
    message = ""
    try:
        conn = pool_map['pool'].acquire()
        db_type = pool_map['db_type']
        conn_map = {
            "conn": conn,
            "db_type": db_type
        }
        logger.debug(f"从连接池中获取数据库连接和数据库类型")
        return conn_map, message
    except Exception as e:
        message = f'获取数据连接异常，错误信息：{e}'
        logger.error(f'获取数据连接异常，错误信息：{e}')
        return None, message


def get_engine():
    url = f'oracle+cx_oracle://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/?service_name={config.DB_NAME}'
    engine = create_engine(url,
                           pool_size=30,
                           max_overflow=20,
                           pool_timeout=30,
                           pool_recycle=1800,
                           pool_pre_ping=True)

    return engine


def close_engine(engine):
    engine.dispose()


def close_conn(pool, conn):
    if isinstance(pool, dict):
        pool = pool['pool']

    if isinstance(conn, dict):
        conn = conn['conn']
    pool.release(conn)
    logger.debug(f"从连接池中释放数据库连接")
    return conn


def commit(conn):
    if isinstance(conn, dict):
        conn = conn['conn']
    conn.commit()
    logger.debug(f"数据库连接-提交事务")
    return


def rollback(conn):
    if isinstance(conn, dict):
        conn = conn['conn']
    conn.rollback()
    logger.debug(f"数据库连接-回滚事务")
    return


def select(conn, sql, params=None):
    result = None
    message = ""
    with conn.cursor() as cursor:
        try:
            if params:
                rs = cursor.execute(sql, params).fetchall()
                result = {
                    'data': rs,
                    'desc': cursor.description
                }
            else:
                rs = cursor.execute(sql).fetchall()
                result = {
                    'data': rs,
                    'desc': cursor.description
                }

            logger.debug(f"[数据查询]sql: {sql}, 参数列表: {params}")

        except Exception as e:
            message = f"[数据查询]异常：{e}"
            logger.error(message)
            return None, message

    # print(result)
    data = []
    for row in result['data']:
        item_map = {}
        for index, item in enumerate(row):
            if result['desc'][index][1] == cx_Oracle.DATETIME and item is not None:
                item = item.strftime("%Y-%m-%d %H:%M:%S")

            item_map[result['desc'][index][0].lower()] = item
        data.append(item_map)
    result['data'] = data
    return result, message


def select_by_map(conn_map, sql, params=None):
    result = None
    message = ""
    conn = conn_map['conn']
    with conn.cursor() as cursor:
        try:
            if params:
                rs = cursor.execute(sql, params).fetchall()
                result = {
                    'data': rs,
                    'desc': cursor.description
                }
            else:
                rs = cursor.execute(sql).fetchall()
                result = {
                    'data': rs,
                    'desc': cursor.description
                }

            logger.debug(f"[数据查询]sql: {sql}, 参数列表: {params}")

            column_types = []
            for desc in result['desc']:
                column_types.append(desc[1])
            result['data_types'] = column_types

        except Exception as e:
            message = f"[数据查询]异常：{e}"
            logger.error(message)
            return None, message

    # print(result)
    data = []
    for row in result['data']:
        item_map = {}
        for index, item in enumerate(row):
            # if result['desc'][index][1] == cx_Oracle.DATETIME and item is not None:
            # 	item = item.strftime("%Y-%m-%d")

            if result['desc'][index][1] == cx_Oracle.TIMESTAMP and item is not None:
                item = item.strftime("%Y-%m-%d %H:%M:%S")

            item_map[result['desc'][index][0].lower()] = item

        data.append(item_map)
    result['data'] = data
    return result, message


def delete(conn, sql, params=None):
    message = ""
    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据删除]sql: {sql}, 参数列表: {params}")
        except Exception as e:
            message = f"[数据删除]异常：{e}"
            logger.error(message)
            return False, message

    return True, message


def delete_by_map(conn_map, sql, params=None):
    message = ""
    conn = conn_map['conn']
    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据删除]sql: {sql}, 参数列表: {params}")
        except Exception as e:
            message = f"[数据删除]异常：{e}"
            logger.error(message)
            return False, message

    return True, message


def update(conn, sql, params=None):
    message = ""
    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据更新]sql: {sql}, 参数列表: {params}")
        except Exception as e:
            message = f"[数据更新]异常：{e}"
            logger.error(message)
            return False, message
    return True, message


def update_by_map(conn_map, sql, params=None):
    message = ""
    conn = conn_map['conn']
    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据更新]sql: {sql}, 参数列表: {params}")
        except Exception as e:
            message = f"[数据更新]异常：{e}"
            logger.info(message)
            return False, message
    return True, message


def insert(conn, sql, params=None):
    message = ""
    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据库新增]sql: {sql}, 参数列表: {params}")

        except Exception as e:
            message = f"[数据库新增]异常：{e}"
            logger.error(message)
            return False, message

    return True, message


def insert_by_map(conn_map, sql, params=None):
    message = ""
    conn = conn_map['conn']
    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据库新增]sql: {sql}, 参数列表: {params}")

        except Exception as e:
            message = f"[数据库新增]异常：{e}"
            logger.error(message)
            return False, message

    return True, message


def insert_by_dataframe(conn_map, df, table_name):
    message = ""
    conn = conn_map
    if isinstance(conn_map, dict):
        conn = conn_map['conn']

    columns = df.columns.tolist()  # 获得dataframe的列名
    data_to_insert = [tuple(row) for row in df.to_numpy()]  # dataframe转换numpy
    print(data_to_insert)
    with conn.cursor() as cursor:
        try:
            sql = df_insert2db(columns, save_table_name=table_name)
            logger.debug(f"[数据库新增][dataframe]sql: {sql}")
            batch_size = int(config.MAP['batch_size'])
            for i in range(0, len(data_to_insert), batch_size):
                batch_data = data_to_insert[i: i + batch_size]
                print(batch_data)
                logger.debug(f"[分批写入][dataframe]当前载入至第{min(i + batch_size, len(data_to_insert))}行。")
                cursor.executemany(sql, batch_data)
                conn.commit()  # 批量执行query_sql, 每批次提交一次

        except Exception as e:
            message = f"[数据库新增][dataframe]异常：{e}"
            logger.error(message)
            conn.rollback()
            return False, message

    return True, message


def df_insert2db(columns, save_table_name):
    """
    Args:
        columns: 以列表的形式
        save_table_name: 保存table的名字
    Returns:直接的insert到Oracle的sql语句，字符串格式
    """
    s = ''
    for i in range(len(columns)):
        s = s + columns[i] + '-'
    sql_columns = s.replace('-', ',')[:-1]  # 不要最后输出的逗号
    sql_number_str = ''
    for i in range(1, len(columns) + 1, 1):
        sql_number_str = sql_number_str + ':' + str(i) + ','  # ':1,:2,:3,:4,:5,:6'
    sql_number_str = sql_number_str[:-1]
    query_sql = 'insert into ' + save_table_name + '(' + sql_columns + ') values(' + sql_number_str + ') '
    return query_sql