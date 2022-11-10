# -*- coding: utf-8 -*-
from dictdiffer import diff
from common.dataFaker import collection
from common.excelManager import readFromExcel
from common.globalVar import globalVar


def generateCase(apiInfoDict):
    caseDict = apiInfoDict.copy()
    for tag, urlInfoDict in caseDict.items():
        for url, methodInfoDict in urlInfoDict.items():
            for method, requestInfoDict in methodInfoDict.items():
                get_url_required_param = False
                if requestInfoDict.get("path"):
                    if requestInfoDict["path"][0]["required"]:
                        get_url_required_param = True
                    requestInfoDict["path"] = fomatCase(requestInfoDict.get("path"), True)
                else:
                    requestInfoDict["path"] = {"Success": [None], "Fail": []}
                if requestInfoDict.get("query"):
                    for i in requestInfoDict["query"]:
                        if i.get("required"):
                            get_url_required_param = True
                    requestInfoDict["query"] = fomatCase(requestInfoDict.get("query"))
                else:
                    requestInfoDict["query"] = {"Success": [None], "Fail": []}
                if requestInfoDict.get("formData"):
                    requestInfoDict["formData"] = fomatCase(requestInfoDict.get("formData"))
                else:
                    requestInfoDict["formData"] = {"Success": [None], "Fail": []}
                if requestInfoDict.get("body"):
                    bodyObject = requestInfoDict.get("body")
                    bodyObjectDict = fomatBodyObj(bodyObject.get("type"),
                                                  bodyObject.get("schema"),
                                                  bodyObject.get("required"))
                    requestInfoDict["body"] = bodyObjectDict
                else:
                    requestInfoDict["body"] = {"Success": [None], "Fail": []}
                generateParamList(requestInfoDict, method, get_url_required_param)
    globalVar.set_value("caseDict", caseDict)
    return caseDict


def fomatCase(paramList, isPath=False):
    paramCaseDict = {}
    # paramCaseList_success = []
    item_success = {}
    paramCaseList_fail = []
    requiredList = []
    for i in range(len(paramList)):
        if paramList[i].get("required"):
            requiredList.append(paramList[i])
            item_success[paramList[i].get("name")] = "collection.availableValue('{}', '{}')".format(
                paramList[i].get("name"), paramList[i].get("type"))
    for paramItem in paramList:
        result_f = generateType(paramItem, requiredList.copy(), isPath)
        # paramCaseList_success.extend(result_s)
        paramCaseList_fail.extend(result_f)
    paramCaseDict["Success"] = [item_success]
    paramCaseDict["Fail"] = paramCaseList_fail
    return paramCaseDict


def generateType(param_item, required_list, isPath):
    case_list_success = []
    case_list_fail = []
    name = param_item.get("name")
    type = param_item.get("type")
    required = False
    if param_item in required_list:
        required = True
        required_list.remove(param_item)
    case_item = {}
    case_item[name] = collection.random_available_value(type)
    for required_item in required_list:
        r_name = required_item.get("name")
        r_type = required_item.get("type")
        r_value = collection.random_available_value(r_type)
        case_item[r_name] = r_value
    case_list_success.append(case_item)

    case_item = {}
    case_item[name] = collection.random_unavailable_value(type)
    for required_item in required_list:
        r_name = required_item.get("name")
        r_type = required_item.get("type")
        r_value = collection.random_available_value(r_type)
        case_item[r_name] = r_value
    case_list_fail.append(case_item)
    if not isPath and required:
        novalue_item, none_item = {}, {}
        novalue_item[name] = ""
        for required_item in required_list:
            r_name = required_item.get("name")
            r_type = required_item.get("type")
            r_value = collection.random_available_value(r_type)
            novalue_item[r_name] = r_value
            none_item[r_name] = r_value
        case_list_fail.append(novalue_item)
        case_list_fail.append(none_item)
    return case_list_fail


# def generateType(param_item, required_list):
#     #生成的用例太多了
#     case_list_success = []
#     case_list_fail = []
#     name = param_item.get("name")
#     type = param_item.get("type")
#     success_value_list = collection.get_available_values(type)
#     fail_value_list = collection.get_unavailable_values(type)
#     if param_item in required_list and type != "file":
#         fail_value_list.append(None)
#         required_list.remove(param_item)
#     for value in success_value_list:
#         case_item = {}
#         case_item[name] = value
#         for required_item in required_list:
#             r_name = required_item.get("name")
#             r_type = required_item.get("type")
#             r_value = collection.random_available_value(r_type)
#             case_item[r_name] = r_value
#         case_list_success.append(case_item)
#     for value in fail_value_list:
#         case_item = {}
#         case_item[name] = value
#         for required_item in required_list:
#             r_name = required_item.get("name")
#             r_type = required_item.get("type")
#             r_value = collection.random_available_value(r_type)
#             case_item[r_name] = r_value
#         case_list_fail.append(case_item)
#     return case_list_success, case_list_fail


def fomatBodyObj(type, obj, required):
    bodyCaseDict = {}
    bodyCase_list_success = []
    bodyCase_list_fail = []
    if type == "array":
        # 列表类型的很少，先只append一个值
        if not required:
            bodyCase_list_success.append([])
        if isinstance(obj, str):
            bodyCase_list_success.append([collection.random_available_value(obj)])
            bodyCase_list_fail.append([collection.random_unavailable_value(obj)])
        else:
            for name, value in obj.items():
                type = value.get("type")
                tmp_obj = {}
                for othername, othervalue in obj.items():
                    if othername == name:
                        continue
                    othertype = othervalue.get("type")
                    tmp_obj[othername] = collection.random_available_value(othertype)
                if list(obj.keys()).index(name) == 0:
                    tmp_obj[name] = collection.random_available_value(type)
                    bodyCase_list_success.append([tmp_obj.copy()])
                tmp_obj[name] = collection.random_unavailable_value(type)
                bodyCase_list_fail.append([tmp_obj])
    else:
        if not required:
            bodyCase_list_success.append({})
        for name, value in obj.items():
            type = value.get("type")
            tmp_obj = {}
            for othername, othervalue in obj.items():
                if othername == name:
                    continue
                othertype = othervalue.get("type")
                if othertype == "array" and othervalue.get("items"):
                    tmp_obj[othername] = collection.random_available_value(othertype,
                                                                           othervalue.get("items").get("type"))
                else:
                    tmp_obj[othername] = collection.random_available_value(othertype)
            if list(obj.keys()).index(name) == 0:
                if type == "array" and value.get("items"):
                    tmp_obj[name] = collection.random_available_value(type, value.get("items").get("type"))
                else:
                    tmp_obj[name] = collection.random_available_value(type)
                bodyCase_list_success.append(tmp_obj.copy())
            if type == "array" and value.get("items"):
                tmp_obj[name] = collection.random_unavailable_value(type, value.get("items").get("type"))
            else:
                tmp_obj[name] = collection.random_unavailable_value(type)
            bodyCase_list_fail.append(tmp_obj.copy())
    bodyCaseDict["Success"] = bodyCase_list_success
    bodyCaseDict["Fail"] = bodyCase_list_fail
    return bodyCaseDict


def generateParamList(requestInfoDict, method, required):
    paramList = []
    n = 1
    operationId = requestInfoDict.get("operationId")
    for path in requestInfoDict.get("path").get("Success") + requestInfoDict.get("path").get("Fail"):
        for query in requestInfoDict.get("query").get("Success") + requestInfoDict.get("query").get("Fail"):
            for formData in requestInfoDict.get("formData").get("Success") + requestInfoDict.get("formData").get(
                    "Fail"):
                for body in requestInfoDict.get("body").get("Success") + requestInfoDict.get("body").get("Fail"):
                    T_path = path in requestInfoDict.get("path").get("Fail")
                    T_query = query in requestInfoDict.get("query").get("Fail")
                    T_form = formData in requestInfoDict.get("formData").get("Fail")
                    T_body = body in requestInfoDict.get("body").get("Fail")
                    T_get_with_mocked_required_param = method == "get" and required
                    T_get_without_mocked_required_param = method == "get" and not required
                    if int(T_path) + int(T_query) + int(T_form) + int(T_body) >= 2:
                        continue
                    paramItem = {}
                    isSuccess = (
                                        not T_path and not T_query and not T_form and not T_body and not T_get_with_mocked_required_param) or (
                                    T_get_without_mocked_required_param)
                    paramItem["caseName"] = "{}_{}".format(operationId, n)
                    paramItem["isSuccess"] = isSuccess
                    paramItem["path"] = path
                    paramItem["query"] = query
                    paramItem["formData"] = formData
                    paramItem["body"] = body
                    n += 1
                    paramList.append(paramItem)
                    requestInfoDict["params"] = paramList
    del requestInfoDict["path"]
    del requestInfoDict["query"]
    del requestInfoDict["formData"]
    del requestInfoDict["body"]


def diffGenerateCase(newApiDict, oldApiDict):
    oldCaseDict = readFromExcel()
    # import json
    # print(json.dumps(oldApiDict))
    # print(json.dumps(newApiDict))
    # print(list(diff(oldApiDict, newApiDict, dot_notation=False)))
    for diffRes in list(diff(oldApiDict, newApiDict, dot_notation=False)):
        opt = diffRes[0]
        pos_list = diffRes[1]
        content_list = diffRes[2]
        if opt == "add":
            pos_len = len(pos_list)
            if pos_len == 0:
                tmpApiDict = {}
                for tag_tuple in content_list:
                    tmpApiDict[tag_tuple[0]] = tag_tuple[1]
                tmpCaseDict = generateCase(tmpApiDict)
                oldCaseDict.update(tmpCaseDict)
            elif pos_len == 1:
                tag = pos_list[0]
                tmpApiDict = {tag: {}}
                for url_tuple in content_list:
                    urlDict = {url_tuple[0]: url_tuple[1]}
                    tmpApiDict[tag].update(urlDict)
                tmpCaseDict = generateCase(tmpApiDict)
                oldCaseDict[tag].update(tmpCaseDict[tag])
            elif pos_len == 2:
                tag = pos_list[0]
                url = pos_list[1]
                tmpApiDict = {tag: {url: {}}}
                for method_tuple in content_list:
                    methodDict = {method_tuple[0]: method_tuple[1]}
                    tmpApiDict[tag][url].update(methodDict)
                tmpCaseDict = generateCase(tmpApiDict)
                oldCaseDict[tag][url].update(tmpCaseDict[tag][url])
            else:
                tag = pos_list[0]
                url = pos_list[1]
                method = pos_list[2]
                tmpApiDict = {
                    tag: {
                        url:
                            {
                                method: newApiDict[tag][url][method]
                            }
                    }
                }
                tmpCaseDict = generateCase(tmpApiDict)
                print(tag, url, method)
                print(oldCaseDict[tag][url][method])
                print(oldCaseDict)
                oldCaseDict[tag][url][method].update(tmpCaseDict[tag][url])
        elif opt == "remove":
            pos_len = len(pos_list)
            if pos_len == 0:
                for tag_tuple in content_list:
                    try:
                        oldCaseDict.pop(tag_tuple[0])
                    except:
                        continue
            elif pos_len == 1:
                tag = pos_list[0]
                for url_tuple in content_list:
                    try:
                        oldCaseDict[tag].pop(url_tuple[0])
                    except:
                        continue
            elif pos_len == 2:
                tag = pos_list[0]
                url = pos_list[1]
                for method_tuple in content_list:
                    try:
                        oldCaseDict[tag][url].pop(method_tuple[0])
                    except:
                        continue
            else:
                tag = pos_list[0]
                url = pos_list[1]
                method = pos_list[2]
                tmpApiDict = {
                    tag: {
                        url:
                            {
                                method: newApiDict[tag][url][method]
                            }
                    }
                }
                tmpCaseDict = generateCase(tmpApiDict)
                oldCaseDict[tag][url][method].update(tmpCaseDict[tag][url])
        else:
            if len(pos_list) < 3:
                print(pos_list, content_list)
                continue
            tag = pos_list[0]
            url = pos_list[1]
            method = pos_list[2]
            tmpApiDict = {
                tag: {
                    url:
                        {
                            method: newApiDict[tag][url][method]
                        }
                }
            }
            tmpCaseDict = generateCase(tmpApiDict)
            oldCaseDict[tag][url][method].update(tmpCaseDict[tag][url])
    globalVar.set_value("caseDict", oldCaseDict)
    return oldCaseDict
