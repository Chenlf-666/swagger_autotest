# -*- coding: utf-8 -*-
import configparser
import re
import requests
import traceback
import xbase64
from requests import request

class ParseConfig:
    def __init__(self):
        self.common_conf = "etc/env.ini"
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config.read(self.common_conf, encoding="utf-8-sig")
        self.report_folder = "report"
        self.case_folder = "testcase"
        self.tmp_folder = "tmp"
        self.excel_folder = "excel"
        self.excel_backup = "backup"
        self.dump_file = "oldAPI.dat"
        self.log_folder = "log"
        self.token = None

    def get_token(self):
        if not self.token:
            return self.basicAuth
        return self.token

    def set_token(self, value):
        self.token = value

    @property
    def swaggerList(self):
        swaggerList = []
        for key in self.config['swaggerUrl']:
            swaggerAPI = self.config.get("swaggerUrl", key)
            swaggerList.append(swaggerAPI)
        return swaggerList

    @property
    def apiPath(self):
        basePath = self.config.get("env", "apiServer")
        return basePath

    @property
    def authPath(self):
        basePath = self.config.get("env", "authServer")
        return basePath

    @property
    def admin_username(self):
        username = self.config.get("env", "adminName")
        return username

    @property
    def admin_password(self):
        password = self.config.get("env", "adminPassword")
        return password

    @property
    def domain(self):
        domain = self.config.get("env", "adminDomain")
        return domain

    @property
    def basicAuth(self):
        adminStr = self.admin_username + ":" + self.admin_password
        astr = adminStr.encode('utf-8')
        admin_token = "Basic " + xbase64.encode(astr)
        return admin_token

    @property
    def headers(self):
        headers = {
            'domain': self.domain,
            'Content-Type': 'application/json'
        }
        return headers

    @property
    def dev_headers(self):
        headers = {
            'domain': self.domain,
            'Content-Type': 'application/json',
            'usertype': "developer"
        }
        return headers



conf = ParseConfig()
