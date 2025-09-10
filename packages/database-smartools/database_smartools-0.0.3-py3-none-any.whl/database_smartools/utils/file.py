# -*- coding: utf-8 -*-

import os
import inspect

def get_file_abspath(file):
    # 获取当前脚本的绝对路径
    file_path = os.path.abspath(file)
    return file_path

def get_file_dir(file_path):
    # 获取脚本所在的目录
    file_dir = os.path.dirname(file_path)
    return file_dir

def search_script(path, filename):
    for root, dirs, files in os.walk(path):
        if filename in files:
            return root, filename
    return None, None
def is_file(obj):
    # 获取脚本所在的目录
    return obj.is_file()

def is_dir(obj):
    # 获取脚本所在的目录
    return obj.is_dir()

def test():
    print(search_script('D:\workspace\python-main\\functions', 'py_test2.py'))

if __name__ == '__main__':
    None
