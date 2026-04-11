# utils.py

import re
import roman
import requests
from bs4 import BeautifulSoup

LAW_NAME_POSTFIX = ("規則", "細則", "辦法", "綱要", "準則", "規程", "標準", "條例", "通則", "法", "律")
MAX_DISCORD_MESSAGE_LEN = 2000
REQUEST_TIMEOUT_SECONDS = 10
REQUEST_HEADERS = {"Connection": "close"}


def law_name_matching(source: str, target: str) -> bool:
    current_location = 0
    for ch in source:
        current_location = target.find(ch, current_location)
        if current_location == -1:
            return False
        current_location += 1
    return True


def remove_law_postfix(name: str) -> str:
    for postfix in LAW_NAME_POSTFIX:
        if name.endswith(postfix):
            name = name[:-len(postfix)]
            break
    return name


def query_str_preprocess(query_str: str) -> list[str | int]:
    query_list: list[str | int] = []
    match_result = re.fullmatch(r'([\u4e00-\u9fff\?]*)([0-9-]*)([IVX]*)', query_str, re.I)
    if not match_result:
        return query_list

    query_list = [token for token in match_result.groups() if token != ""]
    if len(query_list) == 0:
        return query_list

    last_token = query_list[-1]
    if isinstance(last_token, str):
        try:
            query_list[-1] = roman.fromRoman(last_token)
        except (roman.InvalidRomanNumeralError, TypeError):
            pass

    query_list[0] = remove_law_postfix(query_list[0])
    return query_list


def split_msg(resp_message: str) -> list[str]:
    result: list[str] = []
    left = 0
    message_len = len(resp_message)

    if message_len <= MAX_DISCORD_MESSAGE_LEN:
        return [resp_message]

    while left < message_len:
        right = resp_message.rfind("\n", left, min(left + MAX_DISCORD_MESSAGE_LEN, message_len))
        if right == -1 or right < left:
            right = min(left + MAX_DISCORD_MESSAGE_LEN, message_len)
        else:
            right += 1

        result.append(resp_message[left:right])
        left = right
    return result


def requests_get(url: str, *, timeout: float = REQUEST_TIMEOUT_SECONDS, verify: bool = True) -> requests.Response:
    with requests.Session() as session:
        session.keep_alive = False
        response = session.get(url, headers=REQUEST_HEADERS, verify=verify, timeout=timeout)
        response.raise_for_status()
        return response


def soupify(url: str, *, timeout: float = REQUEST_TIMEOUT_SECONDS, verify: bool = True) -> BeautifulSoup:
    response = requests_get(url, timeout=timeout, verify=verify)
    return BeautifulSoup(response.text, "lxml")
