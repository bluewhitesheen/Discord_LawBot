# utils.py

import re
import roman
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def lawNameMatching(s0: str, s1: str):
    currentLocation = 0
    for ch in s0:
        currentLocation = s1.find(ch, currentLocation)
        if currentLocation == -1: return False
    return True

def regulationNameReplacing(s: str):
    lawNamePostfix = ["規則", "細則", "辦法", "綱要", "準則", "規程", "標準", "條例", "通則", "法", "律"]
    for i in lawNamePostfix:
        if s.endswith(i): 
            s = s[:-len(i)]
            break 
    return s

def queryStrPreprocess(queryStr: str):
    queryList = []
    match_result = re.fullmatch('([\u4e00-\u9fff\\?]*)([0-9-]*)([IVX]*)', queryStr, re.I)
    if match_result: 
        queryList = list(match_result.groups())
        if queryList[-1] == '': queryList = queryList[:-1]
    try: 
        queryList[-1] = roman.fromRoman(queryList[-1])
    except: pass
    if len(queryList) == 0: return queryList
    queryList[0] = regulationNameReplacing(queryList[0])
    return queryList

def splitMsg(respMessage: str):
    result = []
    L = 0
    if len(respMessage) < 2000: return [respMessage]
    while L < len(respMessage) - 1:
        R = respMessage.rfind('\n', L, L + 2000)
        result.append(respMessage[L: R+1])
        L = R
    return result

def requestsGet(url: str):
    resp = requests.session()
    resp.keep_alive = False
    resp = resp.get(url, headers={'Connection': 'close'},  verify=False)
    return resp

def lawSoup(url: str):
    resp = requestsGet(url)
    soup = BeautifulSoup(resp.text, "lxml")
    return soup
