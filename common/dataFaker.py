# -*- coding: utf-8 -*-
import os
import random
import sys
from faker import Faker
from common.globalVar import globalVar
from etc.config import conf
from etc.constants import *
from etc.logger import logger

maker = Faker()
cnmaker = Faker(locale='zh_CN')
jpmaker = Faker(locale='ja_JP')
spmaker = Faker(locale='es_ES')

class dataFaker(object):

    def __init__(self):
        self.available_Bool_List = ["true", "false"]

    def random_element(self, _list):
        return maker.random_element(_list)

    @property
    def available_Int_List(self):
        _list = []
        _list.append(0)
        _list.append(-1)
        _list.append(sys.maxsize)
        _list.append(maker.pyint(1, 999999))
        return _list

    @property
    def unavailable_Int_List(self):
        _list = []
        _list.append(maker.word())
        _list.append(sys.maxsize + 1)
        _list.append(maker.pyint(-999999, -2))
        _list.append(maker.pyfloat(right_digits=1, min_value=1, max_value=999999))
        return _list

    @property
    def all_Int_List(self):
        return self.available_Int_List + self.unavailable_Int_List

    def random_available_value(self, _type, list_type=None):
        if _type == "integer":
            _list = self.available_Int_List
            return maker.random_element(_list)
        if _type == "string":
            _list = self.available_Str_List
            return maker.random_element(_list)
        if _type == "boolean":
            _list = self.available_Bool_List
            return maker.random_element(_list)
        if _type == "file":
            return True
        if _type == "number":
            return maker.pyfloat(right_digits=1, min_value=1, max_value=999999)
        if _type == "array":
            if list_type == "integer":
                return maker.pylist(3, True, ["int"])
            if list_type == "string":
                return maker.pylist(3, True, ["str"])
            return maker.pylist(3, True, ["str", "int", "float", "uri", "email"])
        return None

    def random_unavailable_value(self, _type, list_type=None):
        if _type == "integer" or _type == "number":
            _list = self.unavailable_Int_List
            return maker.random_element(_list)
        if _type == "string":
            _list = self.unavailable_Str_List
            return maker.random_element(_list)
        if _type == "boolean":
            _list = self.unavailable_Bool_List
            return maker.random_element(_list)
        if _type == "file":
            return False
        if _type == "array":
            _list = self.unavailable_list_List
            return maker.random_element(_list)

    def get_available_values(self, _type):
        _list = []
        if _type == "integer":
            _list = self.available_Int_List
        if _type == "string":
            _list = self.available_Str_List
        if _type == "boolean":
            _list = self.available_Bool_List
        if _type == "file":
            _list.append(True)
        return _list

    def get_unavailable_values(self, _type):
        _list = []
        if _type == "integer":
            _list = self.unavailable_Int_List
        if _type == "string":
            _list = self.unavailable_Str_List
        if _type == "boolean":
            _list = self.unavailable_Bool_List
        if _type == "file":
            _list.append(False)
        return _list

    @property
    def available_Str_List(self):
        _list = []
        _list.append(maker.password())
        _list.append(maker.pystr(1, 64))
        _list.append(cnmaker.word())
        _list.append(jpmaker.word())
        _list.append(spmaker.word())
        return _list

    @property
    def unavailable_Str_List(self):
        _list = []
        _list.append(maker.pystr(max_chars=1025))
        return _list

    @property
    def all_Str_List(self):
        return self.available_Str_List + self.unavailable_Str_List

    @property
    def unavailable_Bool_List(self):
        _list = []
        _list.append(maker.pyint(3, 100))
        _list.append(maker.word())
        return _list

    @property
    def all_Bool_List(self):
        return self.available_Bool_List + self.unavailable_Bool_List

    @property
    def unavailable_list_List(self):
        _list = []
        _list.append(maker.pystr(1, 64))
        _list.append(maker.pyint(3, 100))
        _list.append(maker.pybool())
        _list.append(maker.pydict(3, True, ["str", "int", "float", "uri", "email"]))
        return _list

    def random_available_file(self, key):
        filename, filepath = self.create_tmp_file(True)
        return (key, (filename, open(filepath, 'rb'), 'application/octet-stream'))

    def random_unavailable_file(self, key):
        filename, filepath = self.create_tmp_file(False)
        return (key, (filename, open(filepath, 'rb'), 'application/octet-stream'))

    def create_tmp_file(self, isempty):
        tmpfolder = conf.tmp_folder
        filename = maker.file_name()
        filepath = os.sep.join([tmpfolder, filename])
        logger.info(filepath)
        if not isempty:
            with open(filepath, "w") as f:
                f.write(maker.pystr(1, 64))
        else:
            open(filepath, "a").close()
        return filename, filepath

    def availableValue(self, key, type):
        # globalVar.show_all()
        if globalVar.get_value(key):
            value_list = globalVar.get_value(key)
            random.shuffle(value_list)
            return value_list.pop()
        else:
            if key in type_list:
                try:
                    value_list = eval(key + ".properties()")
                    return maker.random_element(value_list)
                except:
                    pass
            return self.random_available_value(type)

collection = dataFaker()

