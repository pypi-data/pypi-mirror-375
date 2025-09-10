import sys
import threading

from sqlalchemy import create_engine
import oracledb
from utils import config, logger, texter
import numpy as np
import pandas as pd
import dmPython
from dbutils.persistent_db import PersistentDB
import mysql.connector
import psycopg2
from utils.timer import get_time, get_timediff
from database import dameng_extend as de
from database import oracle_extend as oe
from database import oceanbase_extend as obe
import re
import jaydebeapi

# 获取数据池
POOL_MAP = {}

def _init_lib():
    if "db_lib" in config.MAP.keys():
        lib_dir = config.MAP["db_lib"]
        oracledb.init_oracle_client(lib_dir=lib_dir)

def _init_local_db():
    get_pool_by_key('local')

def get_pool():
    try:
        pool = oracledb.SessionPool(
            user=config.MAP["db_user"],
            password=config.MAP["db_password"],
            dsn=oracledb.makedsn(
                config.MAP["db_host"], config.MAP["db_port"], config.MAP["db_name"]
            ),
            min=2,
            max=15,
            increment=1,
            threaded=False,
        )
    except Exception as e:
        message = f"实例化数据库连接池失败，错误信息：{e}"
        logger.error(message)
        return None, message
    return pool, ""

def get_url(db_key):
    global POOL_MAP
    scan_db_conf = f"""
    			SELECT user_name,pass_word,url FROM task_template_data_source WHERE db_key = :db_key
    			"""
    params = {"db_key": db_key}
    pool_map = POOL_MAP['local']
    conn_map, message = get_conn_map(pool_map)
    logger.debug(f"获取数据源信息，sql:{scan_db_conf}, params: {params}")
    select_result, select_message = select_by_map(conn_map, scan_db_conf, params)
    logger.debug(f"数据源信息:{select_result}")
    if not select_result:
        return None, select_message

    db_conf = select_result["data"][0]
    user_name = db_conf["user_name"]
    pass_word = db_conf["pass_word"]
    url = db_conf["url"]

    url_map = texter.parse_jdbc_url(url)
    url_map["user_name"] = user_name
    url_map["pass_word"] = pass_word
    url_map["url"] = url
    logger.debug(f"数据源配置:{url_map}")
    return url_map

def get_pool_by_key(db_key, refresh=False):
    global POOL_MAP
    pool = None
    logger.debug(f"---------------{__name__}-------------------")
    # print(POOL_MAP)
    if not POOL_MAP and 'local' not in POOL_MAP.keys() and db_key != 'local':
        logger.debug("初始化本地数据库")
        try:
            _init_lib()
        except Exception as e:
            message = f"初始化数据库连接池失败，错误信息：{e}"
            logger.error(message)
        get_pool_by_key('local', refresh=True)

    if db_key not in POOL_MAP.keys() or refresh:
        if db_key == "local":
            url_map = {
                "type": config.MAP["biz_db_type"],
                "host": config.MAP["db_host"],
                "port": config.MAP["db_port"],
                "database": config.MAP["db_name"],
                "user_name": config.MAP["db_user"],
                "pass_word": config.MAP["db_password"],
                "url": config.MAP.get("url")
            }
            logger.debug(f"本地数据库信息：{url_map}")
        else:
            url_map = get_url(db_key)

        if url_map["type"] == "oracle":
            try:
                oracledb.defaults.prefetchrows = int(config.MAP["batch_size"]) + 1
                oracledb.defaults.arraysize = int(config.MAP["batch_size"])
                pool = PersistentDB(
                    creator=oracledb,  # 使用链接数据库的模块
                    maxusage=None,  # 一个链接最多被重复使用的次数，None 表示无限制
                    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                    ping=0,
                    # ping DM 服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it isrequested, 2 = when a cursor is created, 7 = always
                    closeable=False,
                    # 如果为 False 时， conn.close() 实际上被忽略，供下次使用，再线程关闭时，才会自动关闭链接。
                    threadlocal=None,  # 表示 thread-local 数据的类。
                    user=url_map["user_name"],  # 用户名
                    password=url_map["pass_word"],  # 密码
                    dsn=oracledb.makedsn(
                        url_map["host"], url_map["port"], url_map["database"]
                    ),
                )
                # pool = cx_Oracle.SessionPool(user=user_name,
                # 							 password=pass_word,
                # 							 dsn=cx_Oracle.makedsn(url_map['host'], url_map['port'],
                # 												   url_map['database']),
                # 							 min=2, max=15, increment=1, threaded=False)
            except Exception as e:
                message = f"{url_map['type']}实例化数据库连接池失败，错误信息：{e}"
                logger.error(message)

                return None, message

        if url_map["type"] == "dameng":
            try:
                pool = PersistentDB(
                    creator=dmPython,  # 使用链接数据库的模块
                    maxusage=None,  # 一个链接最多被重复使用的次数，None 表示无限制
                    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                    ping=0,
                    # ping DM 服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it isrequested, 2 = when a cursor is created, 7 = always
                    closeable=False,
                    # 如果为 False 时， conn.close() 实际上被忽略，供下次使用，再线程关闭时，才会自动关闭链接。
                    threadlocal=None,  # 表示 thread-local 数据的类。
                    host=url_map["host"],  # 主机号
                    port=url_map["port"],  # 端口号
                    user=url_map["user_name"],  # 用户名
                    password=url_map["pass_word"],  # 密码
                )
            except Exception as e:
                message = f"{url_map['type']}实例化数据库连接池失败，错误信息：{e}"
                logger.error(message)

                return None, message

        if url_map["type"] == "postgresql":
            try:
                pool = PersistentDB(
                    creator=psycopg2,  # 使用链接数据库的模块
                    maxusage=None,  # 一个链接最多被重复使用的次数，None 表示无限制
                    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                    ping=0,
                    # ping DM 服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it isrequested, 2 = when a cursor is created, 7 = always
                    closeable=False,
                    # 如果为 False 时， conn.close() 实际上被忽略，供下次使用，再线程关闭时，才会自动关闭链接。
                    threadlocal=None,  # 表示 thread-local 数据的类。
                    host=url_map["host"],  # 主机号
                    port=url_map["port"],  # 端口号
                    database=url_map["database"],  # 数据库名称
                    user=url_map["user_name"],  # 用户名
                    password=url_map["pass_word"],  # 密码
                )
            except Exception as e:
                message = f"{url_map['type']}实例化数据库连接池失败，错误信息：{e}"
                logger.error(message)

                return None, message

        if url_map["type"] == "mysql":
            try:
                pool = PersistentDB(
                    creator=mysql.connector,  # 使用的 MySQL 驱动
                    maxusage=None,  # 一个链接最多被重复使用的次数，None 表示无限制
                    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                    ping=0,
                    # ping DM 服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it isrequested, 2 = when a cursor is created, 7 = always
                    closeable=False,
                    # 如果为 False 时， conn.close() 实际上被忽略，供下次使用，再线程关闭时，才会自动关闭链接。
                    threadlocal=None,  # 表示 thread-local 数据的类。
                    host=url_map["host"],  # 数据库主机
                    port=url_map["port"],  # 端口号
                    user=url_map["user_name"],  # 用户名
                    password=url_map["pass_word"],  # 密码
                    database=url_map["database"],  # 数据库名称
                    autocommit=True,  # 是否自动提交事务
                    charset="utf8mb4",  # 字符集
                )

            except Exception as e:
                message = f"{url_map['type']}实例化数据库连接池失败，错误信息：{e}"
                logger.error(message)

                return None, message

        if url_map["type"] == "oceanbase":
            try:
                pool = PersistentDB(
                    creator=jaydebeapi,  # 使用链接数据库的模块
                    maxusage=None,  # 一个链接最多被重复使用的次数，None 表示无限制
                    setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
                    ping=0,
                    # ping DM 服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it isrequested, 2 = when a cursor is created, 7 = always
                    closeable=False,
                    # 如果为 False 时， conn.close() 实际上被忽略，供下次使用，再线程关闭时，才会自动关闭链接。
                    threadlocal=None,  # 表示 thread-local 数据的类。
                    jclassname=config.MAP["driver"],  # 数据库驱动类名
                    url=url_map["url"],  # 数据库连接字符串
                    driver_args=[url_map["user_name"], url_map["pass_word"]],  # 驱动参数
                    jars=config.MAP["jar_file"],  # jar包位置
                )

            except Exception as e:
                message = f"{url_map['type']}实例化数据库连接池失败，错误信息：{e}"
                logger.error(message)
                return None, message

        POOL_MAP[db_key] = {"pool": pool, "db_type": url_map["type"]}
        logger.debug(f"创建新的连接池，db_key: {db_key}")
    else:
        pool = POOL_MAP[db_key]["pool"]
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
        message = f"获取数据连接异常，错误信息：{e}"
        logger.error(f"获取数据连接异常，错误信息：{e}")
        return None, message


def get_conn_map(pool_map):
    message = ""
    conn_map = None

    def get_connection():
        nonlocal conn_map
        try:
            conn = pool_map["pool"].connection()
            db_type = pool_map["db_type"]
            cursor = conn.cursor()
            conn_map = {"conn": conn, "db_type": db_type, "cursor": cursor}
            logger.debug(f"从连接池中获取数据库连接和数据库类型")
        except Exception as e:
            nonlocal message
            message = f"获取数据连接异常，错误信息：{e}"
            logger.error(f"获取数据连接异常，错误信息：{e}")

    # 假设超时时间为 10 秒，可根据实际情况调整
    timeout = max(int(config.MAP.get('db_overtime')), 30)
    thread = threading.Thread(target=get_connection)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        message = f"获取数据连接超时，超时时间：{timeout} 秒"
        logger.error(message)
        raise TimeoutError(message)

    return conn_map, message

def get_engine():
    url = f"oracle+cx_oracle://{config.MAP['db_user']}:{config.MAP['db_password']}@{config.MAP['db_host']}:{config.MAP['db_port']}/?service_name={config.MAP['db_name']}"
    engine = create_engine(
        url,
        pool_size=30,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

    return engine


def close_engine(engine):
    engine.dispose()


def close_conn(pool, conn):
    if isinstance(pool, dict):
        pool = pool["pool"]

    if isinstance(conn, dict):
        conn = conn["conn"]
        conn.close()
        logger.debug(f"从连接池中释放数据库连接")
        return conn

    pool.release(conn)
    logger.debug(f"从连接池中释放数据库连接")
    return conn


def commit(conn):
    if isinstance(conn, dict):
        conn = conn["conn"]
    conn.commit()
    logger.debug(f"数据库连接-提交事务")
    return


def rollback(conn):
    if isinstance(conn, dict):
        conn = conn["conn"]
    try:
        conn.rollback()
    except Exception as e:
        logger.warning(f"[数据库连接]回滚异常：{e}")
    logger.debug(f"数据库连接-回滚事务")
    return


def select(conn, sql, params=None):
    result = None
    message = ""
    with conn.cursor() as cursor:
        try:
            logger.debug(f"[数据查询]sql: {sql}, 参数列表: {params}")
            if params:
                rs = cursor.execute(sql, params)
                data = rs.fetchall()
                result = {"data": data, "desc": cursor.description}
            else:
                rs = cursor.execute(sql)
                data = rs.fetchall()
                result = {"data": data, "desc": cursor.description}

        except Exception as e:
            message = f"[数据查询]异常：{e}"
            logger.error(message)
            return None, message

    data = []
    for row in result["data"]:
        item_map = {}
        for index, item in enumerate(row):
            if result["desc"][index][1] == oracledb.DATETIME and item is not None:
                item = item.strftime("%Y-%m-%d %H:%M:%S")

            item_map[result["desc"][index][0].lower()] = item
        data.append(item_map)
    result["data"] = data
    return result, message


def select_by_map(conn_map, sql, params=None):
    result = None
    message = ""
    conn = conn_map["conn"]
    db_type = conn_map["db_type"]
    if db_type == "oceanbase":
        sql, params = map_named_to_positional_params(sql, params)
    #     result, message = obe.execute_select(conn, sql, params)
    #     return result, message

    with conn.cursor() as cursor:
        try:
            logger.debug(f"[数据查询]sql: {sql}, 参数列表: {params}")
            if params:
                cursor.execute(sql, params)
                rs = cursor.fetchall()
                result = {"data": rs, "desc": cursor.description}
            else:
                cursor.execute(sql)
                rs = cursor.fetchall()
                result = {"data": rs, "desc": cursor.description}

            column_types = []
            for desc in result["desc"]:
                column_types.append(desc[1])
            result["data_types"] = column_types

        except Exception as e:
            message = f"[数据查询]异常：{e}"
            # logger.error(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return None, message

    # print(result)
    # 将result["desc"] 的达梦数据类型转成Python的数据类型
    start_time = get_time()
    # if result['desc'][index][1] == cx_Oracle.DATETIME and item is not None:
    # 	item = item.strftime("%Y-%m-%d")
    if db_type == "dameng":
        result["data"] = de.formatter(result)
    if db_type == "oracle":
        result["data"] = oe.formatter(result)
    if db_type == "oceanbase":
        result["data"] = obe.formatter(result)

    end_time = get_time()
    logger.debug(f"重构数据用时：{get_timediff(end_time, start_time)}")
    return result, message


def delete(conn, sql, params=None):
    message = ""
    with conn.cursor() as cursor:
        try:
            logger.debug(f"[数据删除]sql: {sql}, 参数列表: {params}")
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

        except Exception as e:
            message = f"[数据删除]异常：{e}"
            logger.error(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message

    return True, message


def delete_by_map(conn_map, sql, params=None):
    message = ""
    conn = conn_map["conn"]
    db_type = conn_map["db_type"]
    if db_type == "oceanbase":
        sql, params = map_named_to_positional_params(sql, params)

    with conn.cursor() as cursor:
        try:
            logger.debug(f"[数据删除]sql: {sql}, 参数列表: {params}")
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

        except Exception as e:
            message = f"[数据删除]异常：{e}"
            logger.error(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message

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
            logger.debug(f"[数据更新]sql: {sql}, 参数列表: {params}")
            logger.error(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message
    return True, message


def update_by_map(conn_map, sql, params=None):
    message = ""
    conn = conn_map["conn"]
    db_type = conn_map["db_type"]
    if db_type == "oceanbase":
        result, message = map_named_to_positional_params(sql, params)

    with conn.cursor() as cursor:
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            logger.debug(f"[数据更新]sql: {sql}, 参数列表: {params}")
        except Exception as e:
            message = f"[数据更新]异常：{e}"
            logger.debug(f"[数据更新]sql: {sql}, 参数列表: {params}")
            logger.info(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message
    return True, message


def insert(conn, sql, params=None):
    message = ""
    with conn.cursor() as cursor:
        try:
            logger.debug(f"[数据库新增]sql: {sql}, 参数列表: {params}")
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

        except Exception as e:
            message = f"[数据库新增]异常：{e}"
            logger.error(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message

    return True, message


def insert_by_map(conn_map, sql, params=None):
    message = ""
    conn = conn_map["conn"]
    db_type = conn_map["db_type"]
    if db_type == "oceanbase":
        sql, params = map_named_to_positional_params(sql, params)

    with conn.cursor() as cursor:
        try:
            if db_type == "oceanbase":
                set_sql = "set session nls_timestamp_format='YYYY-MM-DD HH24:MI:SS.XFF3'"
                cursor.execute(set_sql)
                set_sql = "set session nls_date_format='YYYY-MM-DD'"
                cursor.execute(set_sql)

            logger.debug(f"[数据库新增]sql: {sql}, 参数列表: {params}")
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

        except Exception as e:
            message = f"[数据库新增]异常：{e}"
            logger.error(message)
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message

    return True, message


def insert_by_dataframe(conn_map, df, table_name):
    message = ""
    conn = conn_map
    db_type = conn_map["db_type"]
    if isinstance(conn_map, dict):
        conn = conn_map["conn"]

    columns = df.columns.tolist()  # 获得dataframe的列名
    # 新增空值处理逻辑
    data_to_insert = [
        tuple(None if pd.isna(value) else value for value in row)
        for row in df.to_numpy(dtype=object)
    ]

    with conn.cursor() as cursor:
        try:
            if db_type == "oceanbase":
                set_sql = "set session nls_timestamp_format='YYYY-MM-DD HH24:MI:SS.XFF3'"
                cursor.execute(set_sql)
                set_sql = "set session nls_date_format='YYYY-MM-DD'"
                cursor.execute(set_sql)
            sql = df_insert2db(columns, save_table_name=table_name)

            logger.debug(f"[数据库新增][dataframe]sql: {sql}")
            batch_size = int(config.MAP["batch_size"])
            for i in range(0, len(data_to_insert), batch_size):
                batch_data = data_to_insert[i : i + batch_size]
                logger.debug(
                    f"[分批写入][dataframe]当前载入至第{min(i + batch_size, len(data_to_insert))}行。"
                )
                print(batch_data[0])
                if db_type == "oceanbase":
                    sql = re.sub(r':\w+', '?', sql)

                cursor.executemany(sql, batch_data)
                conn.commit()  # 批量执行query_sql, 每批次提交一次

        except Exception as e:
            message = f"[数据库新增][dataframe]异常：{e}"
            logger.error(message)
            # if len(batch_data) > 0:
            #     logger.error(f"[数据库新增][dataframe]异常批次数据：{batch_data}")
            try:
                conn.rollback()
            except:
                logger.warning("[数据库新增]回滚异常：{e}")
            raise
            # return False, message

    return True, message


def df_insert2db(columns, save_table_name):
    """
    Args:
        columns: 以列表的形式
        save_table_name: 保存table的名字
    Returns:直接的insert到Oracle的sql语句，字符串格式
    """
    s = ""
    for i in range(len(columns)):
        s = s + columns[i] + "-"
    sql_columns = s.replace("-", ",")[:-1]  # 不要最后输出的逗号
    sql_number_str = ""
    for i in range(1, len(columns) + 1, 1):
        sql_number_str = sql_number_str + ":" + str(i) + ","  # ':1,:2,:3,:4,:5,:6'
    sql_number_str = sql_number_str[:-1]
    query_sql = (
        "insert into "
        + save_table_name
        + "("
        + sql_columns
        + ") values("
        + sql_number_str
        + ") "
    )
    return query_sql

def map_named_to_positional_params(sql, param_dict):
    """
    将带有命名参数的 SQL 转换为使用 ? 占位符的 SQL，
    并生成相应的参数列表
    """
    # 查找所有命名参数
    if param_dict is None:
        return sql, None
    param_names = re.findall(r':(\w+)', sql)

    # 替换命名参数为 ? 占位符
    positional_sql = re.sub(r':\w+', '?', sql)

    # 根据参数名生成参数列表
    param_list = [param_dict[name] for name in param_names]

    return positional_sql, param_list