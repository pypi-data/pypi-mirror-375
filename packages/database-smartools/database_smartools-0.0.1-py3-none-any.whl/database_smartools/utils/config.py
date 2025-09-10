# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : config.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

import configparser

MAP = {}

def add_conf(key, value):
    global MAP
    MAP[key] = value

class Config(object):
    env : str
    def __init__(self, filename, encoding, env):
        print("初始化配置信息")
        global MAP
        MAP = {}
        # 声明配置类对象
        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read(filename, encoding)

        try:
            items = self.get_items('common')
            for key, conf in items:
                setattr(self, key, conf)

            items = self.get_items(env)
            for key, conf in items:
                setattr(self, key, conf)
                if key == 'biz_db_type':
                    db_confs = self.get_items(conf)
                    for key, conf in db_confs:
                        setattr(self, key, conf)

            MAP = self.__dict__
            # print("配置对象属性", MAP)
        except Exception as e:
            print(e)

    def get_options(self, section):
        """获取 option"""
        return self.config.options(section)

    def get_items(self, section):
        """获取 items"""
        return self.config.items(section)

