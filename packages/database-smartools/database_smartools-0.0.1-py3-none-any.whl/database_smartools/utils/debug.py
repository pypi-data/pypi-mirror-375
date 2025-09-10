# -*- coding: utf-8 -*-
"""
@项目名称 : yhfin-data-agent
@文件名称 : debug.py
@创建人   : zhongbinjie
@创建时间 : 2025/9/9 15:24
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""
from utils import logger, config, file, http
import pandas as pd
from utils.timer import get_time, get_timediff
import inspect  # 添加inspect模块导入
import os

def get_caller_file_path(level=1):
    """
    获取调用当前函数的文件路径
    :param level: 调用栈层级，默认为1（直接调用者）
    :return: 调用文件的绝对路径
    """
    try:
        # 获取调用栈信息
        stack = inspect.stack()
        if len(stack) > level + 1:
            # 获取调用者的帧信息
            caller_frame = stack[level + 1]
            # 获取调用者文件路径并转换为绝对路径
            return file.get_file_abspath(caller_frame.filename)
        return None
    except (IndexError, AttributeError):
        return None

def debug_script(obj, params, env="dev"):
    func_file = get_caller_file_path()
    workspace = file.get_file_dir(file.get_file_abspath(func_file))
    cf = config.Config(os.path.join(workspace, "conf.ini"), "UTF-8", env)
    config.add_conf("env", env)
    config.add_conf("root", workspace)
    print(config.MAP)
    logger.Logger()
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_rows', None)
    logger.info("执行接口开始")
    start_time = get_time()
    map = obj(params)
    end_time = get_time()
    logger.info(f"用时：{get_timediff(end_time, start_time)}")
    logger.info("执行接口结束")

def test():
    print()


if __name__ == '__main__':
    None
