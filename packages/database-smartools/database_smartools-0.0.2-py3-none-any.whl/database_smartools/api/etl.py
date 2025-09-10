# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : etl.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

from fastapi import APIRouter
from utils import logger, http
import json
from module import function as func
from database import db_handler as dh

router = APIRouter()

#mcp function call格式
"""
模板样例：
[
        {
                "id": "call_xxxx", #必填项
                "type": "function", #必填项
                "function": {
                        "name": "", #必填项
                        "description": "", #必填项，简要描述
                        "script_path": "", #选填项
                        "input_schema": { #选填项，可以没有参数列表
                                "title": "xxxxx_arguments", #如果有参数列表，则必填项
                                "type": "object", #如果有参数列表，则必填项
                                "properties": { 
                                        "arg1": {"type" : '', "value" : ''}, #如果有参数列表，则必填项，结构保持一致
                                        "arg2": {"type" : '', "value" : ''}
                                },
                                "required": [
                                        "arg1"   #required为选填项，指properties里有的参数为必选参数，值不能为空
                                ]
                        }
                }
        }
]
实际样例：
[
    {
        "id": "wf_pytest",
        "type": "function",
        "function": {
            "name": "py_test2",
            "description": "Function for testing purposes",
            "script_path": "",
            "input_schema": {
                "title": "pytest_arguments",
                "type": "object",
                "properties": {
                    "db_key" : {
                        "type": "string",
                        "value": "123"
                    },
                    "p_beg_date": {
                        "type": "string",
                        "value": "20180101"
                    },
                    "p_end_date": {
                        "type": "string",
                        "value": "20180131"
                    },
                    "p_cal_code": {
                        "type": "string",
                        "value": "400007"
                    }
                },
                "required": [
                    "db_key",
                    "p_beg_date",
                    "p_end_date"
                ]
            }
        }
    }
]
"""
@router.get("/functionCall")
def function_call(function_str: str):
    return_list = []
    #支持工作流：任务1>>任务2串联方式
    try:
        function_map = json.loads(function_str)
        for function in function_map:
            workflow_id = function['id']
            sub_functions = function['function']['name'].split('>>')
            properties = function['function']['input_schema']['properties']
            requires = function['function']['input_schema']['required']
            script_path = None
            if 'script_path' in function['function'].keys():
                script_path = function['function']['script_path']
            args = {}
            for key, param in properties.items():
                if key in requires and (not param['value'] or param['value'] == ""):
                    message = f"缺少必要参数:{key}"
                    logger.error(message)
                    return http.ResponseUtil.error(message=message)
                args[key] = param['value']

            for sub in sub_functions:
                rtn_map = func.execute_function(sub, args, script_path)
                exec_time = rtn_map['time']
                if not rtn_map['status']:
                    return_list.append(http.ResponseUtil.error(message=rtn_map['message'], workflow_id=workflow_id, function=sub, exec_time=exec_time))
                else:
                    data = rtn_map['data']
                    return_list.append(http.ResponseUtil.success(data=data, workflow_id=workflow_id, function=sub, exec_time=exec_time))

    except json.JSONDecodeError:
        message = f"json格式异常，请检查参数：{function_str}"
        logger.error(message)
        return_list.append(http.ResponseUtil.error(message=message))
        return http.ResponseUtil.error(message=message)

    return return_list

@router.get("/dbpool/refresh")
def refresh_dbpool(db_key: str):
    if db_key:
        if db_key not in dh.POOL_MAP.keys():
            return http.ResponseUtil.error(message=f'刷新失败，数据池中没有{db_key}对应的连接')
        else:
            pool, message = dh.get_pool_by_key(db_key, refresh=True)
            if not pool:
                return http.ResponseUtil.error(message=message)

    return http.ResponseUtil.success(message=f"数据库连接池刷新成功，db_key: {db_key}")

@router.get("/logs")
def grap_log(id: str = None):
    message_id = id
    log_file = logger.LOG_NAME
    logs = []
    with open(log_file, "r", encoding="utf-8") as file:
        for line in file:
            try:
                log = json.loads(line.strip())
                if log['id'] == message_id and message_id is not None:
                    logs.append(log)
                if not message_id:
                    logs.append(log)

            except json.JSONDecodeError:
                None
    logger.info(f"抓取日志信息成功，message_id:{id}")
    return http.ResponseUtil.success(data={'logs' : logs})

def test():
    print()


if __name__ == '__main__':
    None
