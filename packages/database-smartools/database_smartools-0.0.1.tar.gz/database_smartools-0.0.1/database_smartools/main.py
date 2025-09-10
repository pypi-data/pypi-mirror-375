# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : main.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""
import multiprocessing

import uvicorn
import sys
from fastapi import FastAPI, Request
from utils import config, file, logger, http, texter, output, timer
from api import etl
import os

app = FastAPI()
env = "dev"
res_dir = os.path.dirname(__file__)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(res_dir)
    print("当前工作路径：", BASE_DIR)
else:
    BASE_DIR = os.path.dirname(__file__)
    print("当前工作路径：", BASE_DIR)

workspace = BASE_DIR
@app.get("/")
def read_root(request: Request):
    return

@app.post("/logRefresh")
def refresh_log():
    logger.Logger()._check_and_rotate_log(refresh=True)
    return http.ResponseUtil.success()

@app.post("/configRefresh")
def refresh_config():
    config.Config(res_dir + '/conf.ini', 'UTF-8', env)
    config.add_conf('env', env)
    config.add_conf('root', workspace)
    logger.Logger()._check_and_rotate_log(refresh=True)
    return http.ResponseUtil.success()

# uvicorn提供服务化
if __name__ == '__main__':
    print(
    rf"""
__   __ _   _  _____  ___  _   _ 
\ \ / /| | | ||  ___||_ _|| \ | |
 \ V / | |_| || |_    | | |  \| |
  | |  |  _  ||  _|   | | | |\  |
  |_|  |_| |_||_|    |___||_| \_|
@项目名称 : python-main
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""
)
    multiprocessing.freeze_support()  # 使用pyinstaller打包后，如果不加这行代码，并行处理会出问题
    argv = sys.argv
    env = 'dev'
    if len(argv) > 1:
        env = argv[1]

    cf = config.Config(res_dir + '/conf.ini', 'UTF-8', env)
    config.add_conf('env', env)
    config.add_conf('root', workspace)
    host = config.MAP['server_host'] if config.MAP['server_host'] != '0.0.0.0' else http.get_local_ip()
    port = int(config.MAP['server_port'])
    logger.Logger()
    from database import db_handler as dh
    dh._init_lib()
    dh._init_local_db()
    logger.debug(f"初始化oracle lib")
    logger.debug(f"----- 工作路径：{workspace} -----")
    logger.debug(f"----- 服务器启动，连接地址 http://{host}:{port} -----")
    logger.debug(f"----- Swagger UI，连接地址 http://{host}:{port}/docs -----")

    from api import etl

    app.include_router(etl.router, prefix="/etl", tags=["ETL工具"])

    uvicorn.run(app, host=host, port=port)
