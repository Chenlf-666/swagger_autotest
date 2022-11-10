# -*- coding: utf-8 -*-
import os
import logging
import unicodedata
from logging.handlers import RotatingFileHandler
from etc.config import conf


class MyLogger:
    def __init__(self, filename='test.log'):
        if not os.path.exists(conf.log_folder):
            os.mkdir(conf.log_folder)
        filename = os.sep.join([conf.log_folder, filename])
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(logging.DEBUG)
        # 设置日志格式
        # print(self.logger.handlers)
        if not self.logger.handlers:
            self.manageHandler(filename)

    def manageHandler(self, filename):
        fmtHandler = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)s][%(levelname)s] %(message)s')

        # 终端log输出流设置
        try:
            consoleHd = logging.StreamHandler()
            consoleHd.setLevel(logging.INFO)
            consoleHd.setFormatter(fmtHandler)
            self.logger.addHandler(consoleHd)
        except Exception as reason:
            self.logger.error("%s" % reason)

        # 设置log文件
        # try:
        #     os.makedirs(os.path.dirname(filename))
        # except Exception as reason:
        #     self.logger.error("%s" % reason)
        # try:
        #     fileHd = logging.FileHandler(filename, "a")
        #     fileHd.setLevel(logging.INFO)
        #     fileHd.setFormatter(fmtHandler)
        #     self.logger.addHandler(fileHd)
        # except Exception as reason:
        #     self.logger.error("%s" % reason)

        # 设置回滚日志,每个日志最大10M,最多备份5个日志
        try:
            rtfHandler = RotatingFileHandler(
                filename, maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8')
            rtfHandler.setLevel(logging.DEBUG)
            rtfHandler.setFormatter(fmtHandler)
            self.logger.addHandler(rtfHandler)
        except Exception as reason:
            self.logger.error("%s" % reason)


    def info(self, msg):
        try:
            self.logger.info(unicodedata.normalize('NFKC', msg))
        except:
            self.logger.info(msg)

    def warn(self, msg):
        try:
            self.logger.warning(unicodedata.normalize('NFKC', msg))
        except:
            self.logger.warning(msg)

    def error(self, msg):
        try:
            self.logger.error(unicodedata.normalize('NFKC', msg))
        except:
            self.logger.error(msg)

    def debug(self, msg):
        try:
            self.logger.debug(unicodedata.normalize('NFKC', msg))
        except:
            self.logger.debug(msg)

logger = MyLogger().logger

# if __name__ == '__main__':
#     logger = MyLogger()
#     text='{"resultCode":997,"message":"Malformed\xa0or illegal\xa0request"}'
#     textb="Your request is invalid, please try again or contact marketplace administrator"
#     logger.info(unicodedata.normalize('NFKC', text))