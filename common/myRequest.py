# -*- coding: utf-8 -*-
import re
import json
import requests
from requests import request
from common.dataFaker import collection
from common.globalVar import globalVar
from etc.logger import logger
from etc.config import conf
from etc.constants import step_one, step_two


def myRequest(url, method, **kwargs):
    if url.startswith("/p-market-web/v1/developers"):
        headers = conf.dev_headers.copy()
    else:
        headers = conf.headers.copy()
    headers["Authorization"] = conf.token

    wholeurl = conf.apiPath + url
    if kwargs.get("path"):
        pathInfo = kwargs.get("path")
        keys = re.findall(r"({\w+})", wholeurl)
        for key in keys:
            keyword = re.search(r"{(\w+)}", key).group(1)
            value = str(pathInfo.get(keyword))
            wholeurl = wholeurl.replace(key, value)

    if kwargs.get("query"):
        param = kwargs.get("query")
    else:
        param = {}

    body = kwargs.get("body")
    form = kwargs.get("formData")
    if body:
        payload = json.dumps(body)
    else:
        payload = json.dumps({})

    tag = kwargs.get("tag")
    operationId = kwargs.get("desc")
    caseName = kwargs.get("caseName")
    if method == "get":
        r = request(method, wholeurl, params=param, headers=headers)
        if operationId in list(step_one.keys()) + list(step_two.keys()):
            need_key = step_one.get(operationId) or step_two.get(operationId)
            try:
                response = r.json(encoding="utf-8")
                need_value = find_possible_value(response)
                if need_value:
                    globalVar.add_value_list(need_key, need_value)
            except:
                pass

    else:
        if form:
            del headers["Content-Type"]
            payload = {}
            files = []
            for key, value in form.items():
                if isinstance(value, bool):
                    if value:
                        files.append(collection.random_available_file(key))
                    else:
                        files.append(collection.random_unavailable_file(key))
                else:
                    payload[key] = value
            r = request(method, wholeurl, params=param, data=payload, files=files, headers=headers)
        else:
            r = request(method, wholeurl, params=param, data=payload, headers=headers)

    logger.info(method.upper() + " " + r.url)
    if body:
        logger.info(body)
    if form:
        logger.info(payload)
    logger.info(headers)
    logger.info(r.text)

    updateResponse(r, tag, url, method, caseName)

    return r


def find_possible_value(result):
    if isinstance(result, dict):
        if result.get("id"):
            return result.get("id")
        for key, value in result.items():
            if isinstance(value, list):
                return find_possible_value(result.get(key)[0])
    if isinstance(result, list):
        return find_possible_value(result[0])
    try:
        return re.search(r"[iI]d': (.*?),", str(result)).group(1)
    except:
        return None


def updateResponse(result, tag, url, method, caseName):
    status_code = result.status_code
    try:
        result_json = result.json(encoding="utf-8")
        resultCode = result_json.get("resultCode")
    except:
        resultCode = None
    caseDict = globalVar.get_value("caseDict")
    first_flag = globalVar.get_value("first_flag")
    if caseDict:
        params = caseDict.get(tag).get(url).get(method).get("params")
        for case_item in params:
            if caseName == case_item.get("caseName"):
                if first_flag:
                    case_item["responseCode"] = status_code
                    case_item["resultCode"] = resultCode
                else:
                    case_item["newResCode"] = status_code
                    case_item["newBusCode"] = resultCode
                break
