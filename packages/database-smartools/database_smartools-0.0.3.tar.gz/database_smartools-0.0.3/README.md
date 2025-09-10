# database-smartools

#### 介绍
一个功能全面的数据库操作工具包，提供统一接口支持多种数据库系统，简化数据库连接、查询与管理操作。支持连接池管理、事务处理和跨数据库兼容功能，适用于需要与多数据库交互的Python项目。

#### 软件架构
- **核心模块**：
  - `database/db_handler.py`：数据库连接管理核心类
  - `database/*_extend.py`：各数据库类型的扩展实现（MySQL、Oracle、PostgreSQL等）
  - `utils/`：配置解析、日志记录等辅助工具
- **技术栈**：Python 3.11+、SQLAlchemy、DBUtils连接池

#### 支持数据库类型
- MySQL
- Oracle
- PostgreSQL
- 达梦数据库(Dameng)
-  OceanBase

#### 安装教程
```bash
pip install database-smartools
```

#### 使用说明
```python
# 基本使用示例
from database_smartools.database import db_handler as dh
from database_smartools.utils import logger, output
import pandas as pd
import traceback

    if args["db_key"] not in dh.POOL_MAP.keys():
        dh.get_pool_by_key(args["db_key"])

    pool_map = dh.POOL_MAP[args["db_key"]]

    params = {
        "key": "value"
    }

    conn_map, message = dh.get_conn_map(pool_map)
    if not conn_map:
        result = False
        return output.OutputUtil.map(result=result, message=message)

    try:
        conn = conn_map["conn"]
        # conn_map["db_type"] = "oceanbase"
        # print(conn_map)
        # 日期遍历
        result = True
        logger.info("开始执行，执行参数：")
        logger.info(params)
        df, message = dh.select_by_map(conn_map, "select 'database_smartools' as software from dual", params)
        df = pd.DataFrame(df["data"])
        if not r:
            result = False

    except Exception as e:
        conn.rollback()  # 回滚事务
        # 获取完整堆栈的错误信息
        message = f"接口执行失败!\n完整错误堆栈信息:\n{traceback.format_exc()}"
        logger.error(message)
        result = False
    finally:
        conn.commit()
    dh.close_conn(pool_map, conn_map)
    return output.OutputUtil.map(result=result, message=message)
```

#### Debug示例
```python
# 初始化数据库连接
from functions import t_r_299_result_n
from database_smartools.utils import debug

if __name__ == "__main__":
    params = {
        "db_key": "GB_YFDW_DW",
        "p_jgdm": "70380000",
        "p_file_date": "20240101",
        "ind_type": "D",
        "p_data_guid": "test_cqb",
        "p_fund_type": "08",
        "p_fund_category": "01",
        "p_item_table": "",
        "p_fdate": "20240101"
    }
    debug.debug_script(t_r_299_result_n.t_r_299_result_n, params, 'dev')
```


#### 项目依赖
- SQLAlchemy 2.0.40+
- DBUtils 3.0.0+
- 各数据库驱动（mysql-connector-python、oracledb等）

#### 许可证
MIT License
