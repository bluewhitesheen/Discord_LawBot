# utils.py

import re
import roman
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

LAW_NAME_POSTFIX = ("規則", "細則", "辦法", "綱要", "準則", "規程", "標準", "條例", "通則", "法", "律")


def law_name_matching(source: str, target: str):
    current_location = 0
    for ch in source:
        current_location = target.find(ch, current_location)
        if current_location == -1: return False
    return True


def regulation_name_replacing(name: str):
    for postfix in LAW_NAME_POSTFIX:
        if name.endswith(postfix): 
            name = name[:-len(postfix)]
            break 
    return name


def query_str_preprocess(query_str: str):
    query_list = []
    match_result = re.fullmatch('([\u4e00-\u9fff\\?]*)([0-9-]*)([IVX]*)', query_str, re.I)
    if match_result: 
        query_list = list(match_result.groups())
        if query_list[-1] == '': query_list = query_list[:-1]
    try: 
        query_list[-1] = roman.fromRoman(query_list[-1])
    except: pass
    if len(query_list) == 0: return query_list
    query_list[0] = regulation_name_replacing(query_list[0])
    return query_list


def split_msg(resp_message: str):
    result = []
    left = 0
    if len(resp_message) < 2000: return [resp_message]
    while left < len(resp_message) - 1:
        right = resp_message.rfind('\n', left, left + 2000)
        result.append(resp_message[left: right+1])
        left = right
    return result

def requests_get(url: str):
    session = requests.session()
    session.keep_alive = False
    response = session.get(url, headers={'Connection': 'close'},  verify=False)
    return response


def soupify(url: str):
    response = requests_get(url)
    soup = BeautifulSoup(response.text, "lxml")
    return soup
