# -*- coding: utf-8 -*-

import time
from datetime import datetime
from . import logger

# 时间装饰器，计算函数运行时长
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"文件 {func.__module__} 函数 {func.__name__} 执行时间：{execution_time:.6f} 秒")
        return result
    return wrapper

def get_curdate(format = None):
    t = datetime.now().strftime('%Y-%m-%d')
    if format:
        try:
            t = t.strftime(format)
        except Exception as e:

            return None
    return t

def get_curdatetime(format = None):
    t = datetime.now()
    if format:
        try:
            t = t.strftime(format)
        except Exception as e:

            return None
    return t

def get_time():
    return time.time()

def get_timediff(time1, time2):
    return time1 - time2