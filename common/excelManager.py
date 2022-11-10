# -*- coding: utf-8 -*-
import datetime
import shutil
import os
import numpy as np
import pandas as pd
from etc.config import conf
from common.globalVar import globalVar


def ExcelGenerator(caseInfos):
    cleanDir(conf.excel_folder)
    for tag, urlInfoDict in caseInfos.items():
        descs = []
        urls = []
        methods = []
        isSuccess = []
        paths = []
        querys = []
        formDatas = []
        bodys = []
        caseIds = []
        responseCodes = []
        resultCodes = []
        newResCodes = []
        newBusCodes = []
        for url, methodInfoDict in urlInfoDict.items():

            for method, requestInfoDict in methodInfoDict.items():
                operationId = requestInfoDict.get("operationId")
                if requestInfoDict.get("params"):
                    for paramItem in requestInfoDict.get("params"):
                        descs.append(operationId)
                        urls.append(url)
                        methods.append(method.upper())
                        isSuccess.append(paramItem.get("isSuccess"))
                        paths.append(paramItem.get("path"))
                        querys.append(paramItem.get("query"))
                        formDatas.append(paramItem.get("formData"))
                        bodys.append(paramItem.get("body"))
                        caseIds.append(paramItem.get("caseName"))
                        if globalVar.get_value("first_flag"):
                            responseCodes.append(paramItem.get("responseCode"))
                            resultCodes.append(paramItem.get("resultCode"))
                        else:
                            if paramItem.get("responseCode") is not None:
                                responseCodes.append(paramItem.get("responseCode"))
                            else:
                                responseCodes.append(None)
                            if paramItem.get("resultCode") is not None:
                                resultCodes.append(paramItem.get("resultCode"))
                            else:
                                resultCodes.append(None)
                            if paramItem.get("newResCode") is not None:
                                newResCodes.append(paramItem.get("newResCode"))
                            else:
                                newResCodes.append(None)
                            if paramItem.get("newBusCode") is not None:
                                newBusCodes.append(paramItem.get("newBusCode"))
                            else:
                                newBusCodes.append(None)
        dfData = {
            "desc": descs,
            "id": caseIds,
            "url": urls,
            "method": methods,
            "isSuccess": isSuccess,
            "path": paths,
            "query": querys,
            "formData": formDatas,
            "body": bodys,
            "responseCode": responseCodes,
            "resultCode": resultCodes
        }
        if not globalVar.get_value("first_flag"):
            dfData.update(
                {
                    "newResCode": newResCodes,
                    "newBusCode": newBusCodes
                }
            )
            writeinexcel(tag, dfData, isFirst=False)
        else:
            writeinexcel(tag, dfData)


def writeinexcel(filename, dfData, isFirst=True):
    data = pd.DataFrame(dfData)
    if not os.path.exists(conf.excel_folder):
        os.mkdir(conf.excel_folder)
    filepath = os.path.join(conf.excel_folder, filename + ".xlsx")
    # print(filepath)
    # writer = pd.ExcelWriter(filepath)
    # data.to_excel(writer, sheet_name=sheetname)
    if not isFirst:
        data.style \
            .apply(fmcolor, axis=1, subset=['resultCode', 'newBusCode']) \
            .apply(fmcolor, axis=1, subset=['responseCode', 'newResCode']) \
            .to_excel(filepath)
    else:
        data.to_excel(filepath)


def fmcolor(x, color='red'):
    return np.where(x != x.to_numpy()[0], f"color: {color};background-color:yellow", None)


def cleanDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return
    backupExcel(path)
    for item in os.listdir(path):
        # if not item.startswith("."):
        itempath = os.sep.join([path, item])
        if os.path.isfile(itempath):
            os.remove(itempath)
        else:
            shutil.rmtree(itempath)


def backupExcel(old_path):
    if not os.path.exists(conf.excel_backup):
        os.mkdir(conf.excel_backup)
    dirname = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dirpath = os.sep.join([conf.excel_backup, dirname])
    shutil.copytree(old_path, dirpath)


def readFromExcel(read_path=conf.excel_folder):
    if not os.path.exists(read_path):
        os.mkdir(read_path)
        return {}
    caseDict = {}
    for file in [i for i in os.listdir(read_path) if i.endswith("xlsx")]:
        tag = file.split(".")[0]
        tag_dict = {}
        filepath = os.sep.join([read_path, file])
        data = pd.read_excel(filepath)
        for url in data["url"].unique():
            url_dict = {}
            data_url = data[data["url"] == url]
            for method in data_url["method"].unique():
                method_dict = {}
                data_method = data_url[data_url["method"] == method]
                param_list = []
                for i in range(len(data_method)):
                    param = {}
                    caseName = data_method["id"].values[i]
                    path = eval(data_method["path"].values[i]) if not pd.isnull(data_method["path"].values[i]) else None
                    query = eval(data_method["query"].values[i]) if not pd.isnull(
                        data_method["query"].values[i]) else None
                    formData = eval(data_method["formData"].values[i]) if not pd.isnull(
                        data_method["formData"].values[i]) else None
                    body = eval(data_method["body"].values[i]) if not pd.isnull(data_method["body"].values[i]) else None
                    isSuccess = data_method["isSuccess"].values[i]
                    param["caseName"] = caseName
                    param["path"] = path
                    param["query"] = query
                    param["formData"] = formData
                    param["body"] = body
                    param["isSuccess"] = isSuccess

                    if "newResCode" in data_method.columns:
                        responseCode = data_method["newResCode"].values[i] if not pd.isnull(
                            data_method["newResCode"].values[i]) else None
                    else:
                        responseCode = data_method["responseCode"].values[i] if not pd.isnull(
                            data_method["responseCode"].values[i]) else None
                    if "newBusCode" in data_method.columns:
                        resultCode = data_method["newBusCode"].values[i] if not pd.isnull(
                            data_method["newBusCode"].values[i]) else None
                    else:
                        resultCode = data_method["resultCode"].values[i] if not pd.isnull(
                            data_method["resultCode"].values[i]) else None
                    param["responseCode"] = responseCode
                    param["resultCode"] = resultCode
                    param_list.append(param)
                method_dict["operationId"] = data_method["desc"].values[0]
                method_dict["params"] = param_list
                url_dict[method] = method_dict
            tag_dict[url] = url_dict
        caseDict[tag] = tag_dict
    return caseDict
