# -*- coding: utf-8 -*-
import os
import shutil

from etc.config import conf
from etc.constants import step_one, step_two


def CodeGenerator(caseInfos):
    if not os.path.exists(conf.case_folder):
        os.mkdir(conf.case_folder)
    cleanDir(conf.case_folder)
    for tag, urlInfoDict in caseInfos.items():
        for url, methodInfoDict in urlInfoDict.items():
            for method, requestInfoDict in methodInfoDict.items():
                operationId = requestInfoDict.get("operationId")
                writeInfo = "import pytest, os, sys, datetime\n"
                writeInfo += "from etc.logger import logger\n"
                writeInfo += "from common.dataFaker import collection\n"
                writeInfo += "from common.myAssert import myAssert\n"
                writeInfo += "from common.myRequest import myRequest\n\n"
                writeInfo += "class Test_{}:\n\n".format(operationId)
                writeInfo += "\ttag = '{}'\n\toperationId = '{}'\n\turl = '{}'\n\tmethod = '{}'\n\n".format(tag, operationId, url, method)

                writeInfo += """\tdef setup_class(self):
\t\tlogger.debug("Start TestCase: %s" % self.__name__)\n
\tdef teardown_class(self):
\t\tlogger.debug("End TestCase: %s" % self.__name__)\n\n"""

                # urlmethodInfo = "\t\turl = '{}'\n\t\tmethod = '{}'\n".format(url, method)
                if requestInfoDict.get("params"):
                    for paramItem in requestInfoDict.get("params"):
                        if paramItem.get("isSuccess"):
                            writeInfo += "\t@pytest.mark.flaky(reruns=1)\n"
                            if not paramItem.get("responseCode"):
                                if operationId in step_one.keys():
                                    writeInfo += "\t@pytest.mark.run(order=1)\n"
                                if operationId in step_two.keys():
                                    writeInfo += "\t@pytest.mark.run(order=2)\n"
                        if method == "DELETE":
                            writeInfo += "\t@pytest.mark.run(order=-1)\n"
                        writeInfo += "\tdef test_{}(self):\n".format(paramItem.get("caseName"))
                        writeInfo += "\t\tpath = {}\n".format(str(paramItem.get("path")).replace('"', ''))
                        writeInfo += "\t\tquery = {}\n".format(str(paramItem.get("query")).replace('"', ''))
                        writeInfo += "\t\tformData = {}\n".format(str(paramItem.get("formData")).replace('"', ''))
                        writeInfo += "\t\tbody = {}\n".format(paramItem.get("body"))
                        writeInfo += "\t\tr = myRequest(url=self.url, method=self.method, path=path, query=query, formData=formData, body=body, caseName='{}', desc=self.operationId, tag=self.tag)\n".format(paramItem.get("caseName"))
                        if paramItem.get("responseCode"):
                            expRes = [paramItem.get("responseCode"), paramItem.get("resultCode")]
                            writeInfo += "\t\tassert myAssert(r, True, {})\n\n".format(expRes)
                        else:
                            if paramItem.get("isSuccess"):
                                writeInfo += "\t\tassert myAssert(r, True)\n\n"
                            else:
                                writeInfo += "\t\tassert myAssert(r, False)\n\n"
                writeinfile(tag, operationId, writeInfo)
    writeconftest(conftest_info)

def writeinfile(foldername, filename, writeInfo):
    filename = "test_" + filename
    if not os.path.exists(conf.case_folder):
        os.mkdir(conf.case_folder)
    controllerfolder = os.path.join(conf.case_folder, foldername)
    if not os.path.exists(controllerfolder):
        os.mkdir(controllerfolder)
    initfilepath = os.path.join(controllerfolder, "__init__.py")
    if not os.path.exists(initfilepath):
        open(initfilepath, "w")
    filepath = os.path.join(controllerfolder, filename + ".py")
    if os.path.exists(filepath):
        os.remove(filepath)
    with open(filepath, "wb") as f:
        f.write(writeInfo.encode("utf-8"))

def writeconftest(writeInfo):
    filename = "conftest.py"
    filepath = os.path.join(conf.case_folder, filename)
    with open(filepath, "wb") as f:
        f.write(writeInfo.encode("utf-8"))

def cleanDir(path):
    for item in os.listdir(path):
        # if not item.startswith("."):
        itempath = os.sep.join([path, item])
        if os.path.isfile(itempath):
            os.remove(itempath)
        else:
            shutil.rmtree(itempath)

conftest_info = """# -*- coding: utf-8 -*-
import pytest
import re
import requests
import traceback
from etc.config import conf
from requests import request

@pytest.fixture(scope="session", autouse=True)
def update_token():
    headers = {
        'domain': conf.domain
    }
    url_getCsrf = conf.authPath + "/login"
    try:
        r = request("get", url_getCsrf)
        _csrf = re.search("\\\"_csrf\\\" value=\\\"(.*)\\\"", r.text).group(1)
        cookies = requests.utils.dict_from_cookiejar(r.cookies)
    except:
        print(traceback.format_exc())
        return

    url_loginServer = conf.authPath + "/passport/login"
    payload = "_csrf={}&username={}&password={}&domain={}".format(_csrf, conf.admin_username,
                                                                                  conf.admin_password, conf.domain)
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    try:
        r2 = request("POST", url_loginServer, headers=headers, data=payload, cookies=cookies,
                     allow_redirects=False)
        token = "Bearer " + re.search("#access_token=(.*?)&", r2.headers["Location"]).group(1)
        conf.set_token(token)
    except:
        print(traceback.format_exc())
        return"""