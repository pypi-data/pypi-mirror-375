# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : output.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

import json

class OutputUtil:
    @staticmethod
    def map(data=None, message="执行成功", result=True, **kwargs):
        response = {
            "result": result,
            "message": message,
            "data": data or {},
            **kwargs  # 支持扩展字段（如 timestamp、pagination）
        }
        if 'json' in kwargs:
            response = json.dumps(response, ensure_ascii=False)
        return response

def test():
    print()

if __name__ == '__main__':
    None
