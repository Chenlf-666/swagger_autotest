# -*- coding: utf-8 -*-
from etc.logger import logger
from etc.constants import *

class globalVariable:
    def __init__(self):  # 初始化
        global _global_dict
        _global_dict = {}


    def add_value_list(self, key, value):
        """ 定义一个全局变量 """
        if not _global_dict.get(key):
            _global_dict[key] = []
        if not value in _global_dict[key]:
            _global_dict[key].append(value)

    def set_value(self, key, value):
        _global_dict[key] = value

    def get_value(self, key):
        """ 获得一个全局变量,不存在则返回False """
        try:
            return _global_dict[key]
        except:
            return False

    def show_all(self):
        print(_global_dict)

globalVar = globalVariable()