# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : logger.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

import json
import logging
import logging.handlers
import sys
import os
from utils import config, timer, texter
import time
from datetime import datetime, timedelta
"""
日志等级：
FATAL：致命错误
CRITICAL：特别糟糕的事情，如内存耗尽、磁盘空间为空，一般很少使用
ERROR：发生错误时，如IO操作失败或者连接问题
WARNING：发生很重要的事件，但是并不是错误时，如用户登录密码错误
INFO：处理请求或者状态变化等日常事务
DEBUG：调试过程中使用DEBUG等级，如算法中每个循环的中间状态

日志参数：
 %(levelno)s：打印日志级别的数值
 %(levelname)s：打印日志级别的名称
 %(pathname)s：打印当前执行程序的路径，其实就是sys.argv[0]
 %(filename)s：打印当前执行程序名
 %(funcName)s：打印日志的当前函数
 %(lineno)d：打印日志的当前行号
 %(asctime)s：打印日志的时间
 %(thread)d：打印线程ID
 %(threadName)s：打印线程名称
 %(process)d：打印进程ID
 %(message)s：打印日志信息
"""
# 单例装饰器
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

LOGGER = None
CONSOLE_HANDLER = None
FILE_HANDLER = None
LOG_NAME = ""

class ModuleFilter(logging.Filter):
    def filter(self, record):
        # 仅记录非 INFO 和 WARNING 级别
        return record.levelno not in (logging.INFO, logging.WARNING)

# 使用单例装饰器
@singleton
class Logger:
    def __init__(self):
        print("初始化日志信息")
        self._init_logger()

    def _init_logger(self, name=__name__):
        log_params = {
            "root_path": config.MAP['root'],
            "log_path": config.MAP['log_path'] if 'log_path' in config.MAP else 'logs',
            "log_filename": f"{config.MAP['log_filename']}_{timer.get_curdatetime('%Y%m%d')}.log" if 'log_filename' in config.MAP else f"log_{timer.get_curdatetime('%Y%m%d')}.log",
            "log_level": config.MAP['log_level'] if 'log_level' in config.MAP else 'INFO',
            "log_mode": config.MAP['log_mode'] if 'log_mode' in config.MAP else 'a'
        }
        global LOGGER  # logger对象
        global CONSOLE_HANDLER  # 控制台处理器
        global FILE_HANDLER  # 文件处理器
        if not LOGGER:
            LOGGER = logging.getLogger(name)

        if LOGGER.hasHandlers():
            for handler in LOGGER.handlers[:]:
                LOGGER.removeHandler(handler)

        self._set_log_level(log_params)

        root_path = log_params['root_path']
        log_path = log_params['log_path']
        log_abspath = os.path.join(root_path, log_path)
        # 检查日志目录是否存在
        if not os.path.exists(log_abspath):
            os.mkdir(log_abspath)
        log_filename = log_params['log_filename']
        global LOG_NAME  # log文件
        LOG_NAME = os.path.join(log_abspath, log_filename)
        # 创建处理器 handlers
        # 日志文件大小超过 50MB 时进行轮转，最多保留 10 个备份文件
        log_max_size = config.MAP['log_max_size'] if 'log_max_size' in config.MAP else '50MB'
        FILE_HANDLER = logging.handlers.RotatingFileHandler(
            LOG_NAME,
            encoding='UTF-8',
            maxBytes=texter.convert_to_bytes(log_max_size),
            backupCount=1000  # 一个极大值，近似无上限
        )
        FILE_HANDLER.setLevel(logging.DEBUG)
        CONSOLE_HANDLER = logging.StreamHandler(stream=sys.stdout)  # 输出到控制台
        CONSOLE_HANDLER.setLevel(logging.DEBUG)
        # 创建格式器
        file_format = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', '%Y%m%d-%H:%M:%S')
        console_format = logging.Formatter(
            '[%(levelname)s]' + ' ' * (6 - len(str(CONSOLE_HANDLER.level))) + '%(message)s')
        # 将格式器添加到处理器中
        FILE_HANDLER.setFormatter(file_format)
        CONSOLE_HANDLER.setFormatter(console_format)
        # 添加filter
        CONSOLE_HANDLER.addFilter(ModuleFilter())
        LOGGER.addHandler(CONSOLE_HANDLER)
        # 将处理器添加到logger
        LOGGER.addHandler(FILE_HANDLER)
        # 删除七天前的日志文件
        self._delete_old_logs(log_abspath)

    def _delete_old_logs(self, log_dir):
        save_days = int(config.MAP['log_save_days'])
        save_days_ago = datetime.now() - timedelta(days=save_days)
        for root, dirs, files in os.walk(log_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_mtime < save_days_ago:
                        os.remove(file_path)
                        print(f"删除旧日志文件: {file_path}")
                except Exception as e:
                    print(f"删除文件 {file_path} 时出错: {e}")

    def _set_log_level(self, log_params):
        LOGGER.setLevel(logging.INFO)
        if log_params['log_level'] == 'FATAL':
            LOGGER.setLevel(logging.FATAL)
        elif log_params['log_level'] == 'CRITICAL':
            LOGGER.setLevel(logging.CRITICAL)
        elif log_params['log_level'] == 'ERROR':
            LOGGER.setLevel(logging.ERROR)
        elif log_params['log_level'] == 'WARNING':
            LOGGER.setLevel(logging.WARNING)
        elif log_params['log_level'] == 'INFO':
            LOGGER.setLevel(logging.INFO)
        elif log_params['log_level'] == 'DEBUG':
            LOGGER.setLevel(logging.DEBUG)

    def _check_and_rotate_log(self, refresh=False):
        current_date = timer.get_curdatetime('%Y%m%d')
        expected_log_filename = f"{config.MAP['log_filename']}_{current_date}.log" if 'log_filename' in config.MAP else f"log_{current_date}.log"
        global FILE_HANDLER
        global LOG_NAME
        if expected_log_filename not in LOG_NAME or refresh:
            if refresh: print("重置日志信息")
            # 移除旧的文件处理器
            LOGGER.removeHandler(FILE_HANDLER)
            FILE_HANDLER.close()

            log_params = {
                "root_path": config.MAP['root'],
                "log_path": config.MAP['log_path'] if 'log_path' in config.MAP else 'logs',
                "log_filename": expected_log_filename,
                "log_level": config.MAP['log_level'] if 'log_level' in config.MAP else 'INFO',
                "log_mode": config.MAP['log_mode'] if 'log_mode' in config.MAP else 'a'
            }

            root_path = log_params['root_path']
            log_path = log_params['log_path']
            log_abspath = os.path.join(root_path, log_path)
            if not os.path.exists(log_abspath):
                os.mkdir(log_abspath)
            LOG_NAME = os.path.join(log_abspath, expected_log_filename)

            # 创建新的文件处理器
            log_max_size = config.MAP['log_max_size'] if 'log_max_size' in config.MAP else '50MB'
            FILE_HANDLER = logging.handlers.RotatingFileHandler(
                LOG_NAME,
                encoding='UTF-8',
                maxBytes=texter.convert_to_bytes(log_max_size),
                backupCount=1000  # 一个极大值，近似无上限
            )
            FILE_HANDLER.setLevel(logging.DEBUG)
            file_format = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', '%Y%m%d-%H:%M:%S')
            FILE_HANDLER.setFormatter(file_format)
            LOGGER.addHandler(FILE_HANDLER)
            return log_abspath
        return None

def _log_wrapper(func):
    def wrapper(message, *args, **kwargs):
        log_abspath = Logger()._check_and_rotate_log()
        if log_abspath:
            Logger()._delete_old_logs(log_abspath)
        return func(message, *args, **kwargs)
    return wrapper

@_log_wrapper
def info(message):
    LOGGER.info(message)

@_log_wrapper
def debug(message):
    LOGGER.debug(message)

@_log_wrapper
def warning(message):
    LOGGER.warning(message)

@_log_wrapper
def error(message):
    LOGGER.error(message)

def system(message, id):
    Logger()._check_and_rotate_log()
    file_handler = [handler for handler in LOGGER.handlers if isinstance(handler, logging.FileHandler)][0]
    LOGGER.removeHandler(file_handler)
    log = {
        "timestamp": timer.get_curdatetime('%Y%m%d-%H:%M:%S'),
        "level": "system",
        "id": id,
        "message": message.replace("\n", "\\n")
    }

    file_format = logging.Formatter('')
    FILE_HANDLER.setFormatter(file_format)
    LOGGER.addHandler(FILE_HANDLER)
    LOGGER.debug(json.dumps(log, ensure_ascii=False))


if __name__ == '__main__':
    None

