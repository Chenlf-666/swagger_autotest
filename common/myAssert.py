# -*- coding: utf-8 -*-
from etc.logger import logger
from etc.config import conf
import json
import traceback

def myAssert(result, isSuccess=True, expectResponse=None):
    if expectResponse:
        expResCode = expectResponse[0]
        expBusCode = expectResponse[1]
        if result.status_code == int(expResCode):
            if expBusCode is not None and result.content:
                response = result.content.decode()
                new_response = json.loads(response)
                if new_response.get("resultCode") == int(expBusCode):
                    return True
            elif not expBusCode and not result.content:
                return True
        return False
    else:
        if isSuccess:
            if result.ok:
                return True
            else:
                if result.content:
                    response = result.content.decode()
                    new_response = json.loads(response)
                    if new_response.get("message") and "not found" in new_response.get("message"):
                        return True
                logger.error("Response expected to be Success but Fail")
                return False
        else:
            if result.ok:
                logger.error("Response expected to be Fail but Success")
                return False
            else:
                return True

def compareDict(expectDict, actualDict):
    if len(set(actualDict.keys()) - set(expectDict.keys())) == 0:
        return True
    return False