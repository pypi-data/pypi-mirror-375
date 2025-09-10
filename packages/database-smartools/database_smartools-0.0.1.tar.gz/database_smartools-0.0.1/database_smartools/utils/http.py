# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : http.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

# 200：请求成功的状态码
# 404：页面找不到
# 422：请求体中数据有问题（格式不正确，名字匹配不对）
# 405：请求的方式不匹配（如路径是get形式，但是函数上面写的是其他的请求类型）
# 500：后台服务器程序出错
import socket
import json

class ResponseUtil:
    @staticmethod
    def success(data=None, message="执行成功", code=200, **kwargs):
        """成功响应"""
        response = {
            "code": code,
            "message": message,
            "data": data or {},
            **kwargs  # 支持扩展字段（如 timestamp、pagination）
        }
        if 'json' in kwargs:
            response = json.dumps(response, ensure_ascii=False)
        return response

    @staticmethod
    def error(code=500, message="失败", data=None, errors=None, **kwargs):
        """错误响应"""
        response = {
            "code": code,
            "message": message,
            "data": data or {},
            "errors": errors or {},
            **kwargs  # 支持扩展字段
        }
        if 'json' in kwargs:
            response = json.dumps(response, ensure_ascii=False)
        return response

    @staticmethod
    def empty(message="无数据", code=400):
        """空数据响应"""
        return ResponseUtil.success(data={}, message=message, code=code)

def get_local_ip():
    # 创建一个UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到一个公共的外部IP地址（不会实际发送数据）
        s.connect(('8.8.8.8', 80))
        # 获取连接的本地地址
        ip = s.getsockname()[0]
    except Exception as e:
        print(f"Error occurred: {e}")
        ip = '127.0.0.1'
    finally:
        s.close()

    return ip

def test():
    print()


if __name__ == '__main__':
    None
