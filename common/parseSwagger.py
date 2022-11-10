# -*- coding: utf-8 -*-
import os
import pickle
import requests
from common.globalVar import globalVar
from etc.config import conf
from etc.logger import logger


def getAPIsfromSwagger():
    allAPIDict = {}
    for swaggerUrl in conf.swaggerList:
        try:
            responseJson = requests.get(swaggerUrl, timeout=60).json()
        except:
            logger.error('Get request from {} error!'.format(swaggerUrl))
            continue
        basePath = responseJson.get('basePath')
        paths = responseJson.get('paths')
        definitions = responseJson.get("definitions")
        globalVar.set_value("definitions", definitions)
        if basePath and paths:
            for url in paths.keys():  # url
                urlItem = paths.get(url)
                # apiDict = {"requests": []}
                for method in urlItem.keys():  # get/post
                    # if method != "get":
                    #     continue    #for test
                    methodItem = urlItem.get(method)
                    # 判断该api是否已不再使用
                    if methodItem.get('deprecated') is False or not methodItem.get('deprecated'):
                        methodDict = {}
                        tag = methodItem.get("tags")[0]
                        if allAPIDict.get(tag):
                            pass
                        # methodDict["method"] = method
                        methodDict["operationId"] = methodItem.get("operationId")
                        methodDict["summary"] = methodItem.get("summary")
                        if method == "post":
                            methodDict["Content-Type"] = methodItem.get("consumes")[0]
                        parameters = methodItem.get("parameters")
                        # 获取所有的参数，类型包括path/query/formData/body
                        if parameters:
                            pathList, queryList, formDataList = [], [], []
                            bodyObject = {}
                            for param in parameters:
                                if param.get("name").count("requestHeaders") != 0:
                                    continue
                                paramLoc = param.get("in")
                                if paramLoc != "body":
                                    paramItem = {}
                                    paramItem["name"] = param.get("name")
                                    paramItem["required"] = param.get("required")
                                    paramItem["type"] = param.get("type")
                                    if param.get("format"):
                                        paramItem["format"] = param.get("format")
                                    if paramLoc == "path":
                                        pathList.append(paramItem)
                                    elif paramLoc == "query":
                                        queryList.append(paramItem)
                                    elif paramLoc == "formData":
                                        formDataList.append(paramItem)
                                else:
                                    bodyObject["name"] = param.get("name")
                                    bodyObject["required"] = param.get("required")
                                    if param.get("schema").get("type"):
                                        bodyObject["type"] = param.get("schema").get("type")
                                        if param.get("schema").get("items"):
                                            if param.get("schema").get("items").get("type"):
                                                bodyObject["schema"] = param.get("schema").get("items").get("type")
                                            else:
                                                bodyObject["schema"] = getRefBody(definitions,
                                                                                  param.get("schema").get("items").get(
                                                                                      "$ref"))
                                        else:
                                            bodyObject["schema"] = {}
                                    else:
                                        bodyObject["type"] = "object"
                                        bodyObject["schema"] = getRefBody(definitions, param.get("schema").get("$ref"))
                            if pathList:
                                methodDict["path"] = pathList
                            else:
                                methodDict["path"] = None
                            if queryList:
                                methodDict["query"] = queryList
                            else:
                                methodDict["query"] = None
                            if formDataList:
                                methodDict["formData"] = formDataList
                            else:
                                methodDict["formData"] = None
                            if bodyObject:
                                methodDict["body"] = bodyObject
                            else:
                                methodDict["body"] = None
                        else:
                            methodDict["path"] = None
                            methodDict["query"] = None
                            methodDict["formData"] = None
                            methodDict["body"] = None
                        # responses = methodItem.get("responses")
                        # responseOk = responses.get("200")
                        # if responseOk.get("schema") and not responseOk.get("schema").get("type"):
                        #     methodDict["response"] = getRefBody(definitions, responseOk.get("schema").get("$ref"))
                        # else:
                        #     methodDict["response"] = "None"
                        if allAPIDict.get(tag):
                            tagDict = allAPIDict.get(tag)
                            if tagDict.get(basePath + url):
                                tagDict[basePath + url].update({method: methodDict})
                            else:
                                tagDict[basePath + url] = {}
                                tagDict[basePath + url][method] = methodDict
                        else:
                            allAPIDict[tag] = {}
                            allAPIDict[tag][basePath + url] = {}
                            allAPIDict[tag][basePath + url][method] = methodDict
                        # apiDict["requests"].append(methodDict)

                # allAPIDict[basePath + url] = apiDict

    return allAPIDict


def getRefBody(definitions, key=""):
    key = key.split("/")[-1]
    refInfo = definitions.get(key).get("properties")
    for property, value in refInfo.items():
        # Info中还会有"$ref"字段，转换成array或object
        if str(value).count("'$ref'") != 0:
            if value.get("type"):
                refInfo.update({property: {"type": "array"}})
            else:
                refInfo.update({property: {"type": "object"}})
    return refInfo


def dumpInfo(apiDict):
    if not os.path.exists(conf.excel_backup):
        os.mkdir(conf.excel_backup)
    filepath = os.sep.join([conf.excel_backup, conf.dump_file])
    with open(filepath, "wb") as f:
        pickle.dump(apiDict, f)


def loadInfo():
    filepath = os.sep.join([conf.excel_backup, conf.dump_file])
    with open(filepath, "rb") as f:
        apiDict = pickle.load(f)
    return apiDict
