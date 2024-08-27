# fetch.py

import os, re, requests
from parsel import Selector
from utils import lawSoup

def fetch_cj_numbers():
    BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
    CJArc = os.path.join(BASE_DIR, "res/CJArc")

    cjNum = {} 
    localCJList = os.listdir(CJArc)

    tmpsoup = lawSoup('https://cons.judicial.gov.tw/judcurrentNew1.aspx?fid=38').find('div', class_='judgmentTabCont').find_all('li')
    cjList = [item for item in tmpsoup if len(item.text) > 9]
    for item in cjList:
        year, num = re.findall(r'\d+', item.text)
        id = re.search(r'\d{6}', str(item)).group()
        cjNum[(year, num)] = id

    for filename in localCJList:
        year, num = filename[:3], filename[3:5].lstrip('0')
        if (year, num) in cjNum: 
            del cjNum[(year, num)]
    return cjNum

def fetch_and_save_cj(cjNum, CJArc):
    for year, num in cjNum:
        url = 'https://cons.judicial.gov.tw/docdata.aspx?fid=38&id=' + str(cjNum[(year, num)])
        res = requests.get(url)
        par = Selector(text=res.text)
        lawList = par.css('.lawList')
        respMessage = ["<" + url + ">", ]
        pureNumber = re.compile(r'^\d*$')
        for item in lawList:
            text = item.xpath('.//text()').getall()
            for t in text:
                t = t.strip()
                if len(t) == 0 or pureNumber.match(t) is not None:
                    continue
                elif t == '理由':
                    break
                elif t in ('判決字號', '原分案號', '判決日期', '聲請人', '案由', '主文'):
                    respMessage.append('-' * 46)
                respMessage.append(t)
        with open(os.path.join(CJArc, year + num.zfill(2) + ".txt"), 'w', encoding='utf-8') as f:
            f.write("\n".join(respMessage))

if __name__ == "__main__":
    cjNum = fetch_cj_numbers()
    BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
    CJArc = os.path.join(BASE_DIR, "res/CJArc")
    fetch_and_save_cj(cjNum, CJArc)
    print("Finished fetching: " + str(cjNum))

    # cjNum = {('113', '7'): '346206'}