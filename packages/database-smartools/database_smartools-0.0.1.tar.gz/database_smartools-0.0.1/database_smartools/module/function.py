# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : function.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

import importlib
import os.path
import sys
from pathlib import Path
from utils import logger, config, file, timer


def execute_function(func_name, args=None, script_dir=None):
    """
    通过函数名动态执行对应脚本中的函数

    :param func_name: 要执行的函数名称
    :param args: 函数传入的参数
    :param script_dir: 存放函数脚本的目录，默认为conf.ini -> common -> script_dir
    """
    result = {
        'status': False,
        'data': {},
        'message': f"函数{func_name}运行时发生错误，未知异常",
        'time': 0
    }
    # 获取函数脚本目录的绝对路径
    base_dir = config.MAP['root']  # 当前项目所在目录
    target_dir = os.path.join(base_dir, config.MAP['script_dir'])
    if script_dir:
        target_dir = script_dir
    # 临时添加目标目录到sys.path
    original_sys_path = sys.path.copy()
    start_time = timer.get_time()
    try:

        root, filename = file.search_script(target_dir, func_name + '.py')
        if not root:
            end_time = timer.get_time()
            message = f"错误：找不到名为'{func_name}'的脚本。"
            logger.error(message)
            result['status'] = False
            result['message'] = message
            result['time'] = timer.get_timediff(end_time, start_time)
            return result

        sys.path.insert(0, str(root))

        try:
            # 动态导入模块
            module = importlib.import_module(func_name)

            # 获取函数对象
            func = getattr(module, func_name)
            logger.debug(f"获取函数对象，module: {module}, func_name: {func_name}")

            # 执行函数
            rtn_map = None
            logger.debug(f"运行函数，func_name: {func_name}")
            if args:
                rtn_map = func(args)
            else:
                rtn_map = func()
            end_time = timer.get_time()
            dur_time = timer.get_timediff(end_time, start_time)
            result['time'] = dur_time
            logger.debug(f"函数运行结束，运行时间: {dur_time}")
            if rtn_map is not None:
                result['status'] = rtn_map['result']
                if 'data' in rtn_map.keys():
                    result['data'] = rtn_map['data']
                result['message'] = rtn_map['message']

        except ImportError as e:
            end_time = timer.get_time()
            message = f"脚本'{func_name}'导入异常。错误信息：{e}"
            logger.error(message)
            result['status'] = False
            result['message'] = message
            result['time'] = timer.get_timediff(end_time, start_time)

        except AttributeError as e:
            end_time = timer.get_time()
            message = f"函数{func_name}运行时发生错误，错误信息：{e}。"
            logger.error(message)
            result['status'] = False
            result['message'] = message
            result['time'] = timer.get_timediff(end_time, start_time)

        finally:
            # 从 sys.modules 中移除已导入的模块
            if func_name in sys.modules:
                del sys.modules[func_name]
            # 从 sys.path 中移除临时添加的路径
            if str(root) in sys.path:
                sys.path.remove(str(root))

    except Exception as e:
        end_time = timer.get_time()
        message = f"函数{func_name}运行时发生错误，错误信息：{e}。"
        logger.error(message)
        result['status'] = False
        result['message'] = message
        result['time'] = timer.get_timediff(end_time, start_time)

    finally:
        # 恢复原始sys.path
        sys.path = original_sys_path
        return result
