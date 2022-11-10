# -*- coding: utf-8 -*-
import os
import pytest
import subprocess
import shutil
from common.parseSwagger import *
from common.generateCase import *
from common.generateFile import *
from common.excelManager import *
from etc.config import conf
from etc.logger import logger


def cleanDir(path):
    for item in os.listdir(path):
        item_path = os.sep.join([path, item])
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            shutil.rmtree(item_path)


def check_dir():
    if not os.path.exists(conf.report_folder):
        os.mkdir(conf.report_folder)
        os.mkdir(xml_report_path)
        os.mkdir(html_report_path)
    else:
        if not os.path.exists(xml_report_path):
            os.mkdir(xml_report_path)
        if not os.path.exists(html_report_path):
            os.mkdir(html_report_path)
    if not os.path.exists(conf.tmp_folder):
        os.mkdir(conf.tmp_folder)
    else:
        cleanDir(conf.tmp_folder)


def isFirstRun():
    # judge is the first time to run, 1 means yes
    if os.path.exists(conf.excel_backup):
        bak_path = os.sep.join([conf.excel_backup, conf.dump_file])
        if os.path.exists(bak_path):
            globalVar.set_value("first_flag", False)
            return False
    globalVar.set_value("first_flag", True)
    return True


if __name__ == '__main__':
    help_info = """please input run type
    1 for only generate case files
    2 for run exist cases in testcase folder
    3 for generate case files and then run cases(recommend)
    """
    print(help_info)
    xml_report_path = os.path.join(conf.report_folder, "xml")
    html_report_path = os.path.join(conf.report_folder, "html")
    # run_type = input("Your input: ")
    run_type = "3"
    logger.info("run_type: {}".format(run_type))
    if run_type == "1":
        apiDict = getAPIsfromSwagger()
        dumpInfo(apiDict)
        # print(apiDict)
        caseDict = generateCase(apiDict)
        # ExcelGenerator(caseDict)
        # print(caseDict)
        CodeGenerator(caseDict)
        ExcelGenerator(caseDict)

    elif run_type == "2":
        if not os.path.exists(conf.case_folder):
            print("Case file not exist, please check is testcase folder exist!")
            exit(1)
        check_dir()
        args = ['-s', '-q',
                '--alluredir', xml_report_path, "--clean-alluredir",
                "-W", "ignore:Module already imported:pytest.PytestWarning"]
        pytest.main(args)
        cmd = "allure generate %s -o %s --clean" % (xml_report_path, html_report_path)
        try:
            res = subprocess.check_output(cmd, shell=True)
        except Exception:
            logger.error('执行用例失败，请检查环境配置')
            raise

    elif run_type == "3":
        apiDict = getAPIsfromSwagger()
        if isFirstRun():
            dumpInfo(apiDict)
            caseDict = generateCase(apiDict)
        else:
            oldApiDict = loadInfo()
            dumpInfo(apiDict)
            caseDict = diffGenerateCase(apiDict, oldApiDict)
        # print(caseDict)
        CodeGenerator(caseDict)
        args = ['-s', '-q',
                '--alluredir', xml_report_path, "--clean-alluredir",
                "-W", "ignore:Module already imported:pytest.PytestWarning"]
        pytest.main(args)
        cmd = "allure generate %s -o %s --clean" % (xml_report_path, html_report_path)
        try:
            res = subprocess.check_output(cmd, shell=True)

        except Exception:
            logger.error('执行用例失败，请检查环境配置')
            raise
        ExcelGenerator(caseDict)
    else:
        print("Error input!")
        exit(1)

    if os.path.exists(conf.tmp_folder):
        shutil.rmtree(conf.tmp_folder)
