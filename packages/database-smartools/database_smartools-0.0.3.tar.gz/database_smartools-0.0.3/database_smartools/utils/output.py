# -*- coding: utf-8 -*-

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
