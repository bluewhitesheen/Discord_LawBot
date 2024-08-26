import os, ast, discord, re, requests, roman, time
from parsel import Selector
from dotenv import load_dotenv
from utils import lawNameMatching, regulationNameReplacing, queryStrPreprocess, splitMsg, lawSoup

BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
lawDict = ast.literal_eval(open(os.path.join(BASE_DIR, "res/lawDict.txt"), "r", encoding='utf-8').read())
lawNameDict = open(os.path.join(BASE_DIR, "res/lawName.txt"), "r", encoding='utf-8').readlines()
lawNameDict = {i.split()[0]: i.split()[1] for i in lawNameDict}

# Constitutional Judgement finding function
def CJfind(queryStr):
    queryNum = queryStr[0] + queryStr[2].zfill(2)
    print(queryNum)
    fDir = os.path.join(BASE_DIR, "res/CJArc", str(queryNum) + ".txt")
    if os.path.exists(fDir):
        with open(fDir, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print('The file does not exist.')
        cjNum = {} 
        tmpsoup = lawSoup('https://cons.judicial.gov.tw/judcurrentNew1.aspx?fid=38').find('div', class_ = 'judgmentTabCont').find_all('li')
        cjList = [item for item in tmpsoup if len(item.text) > 9]
        for item in cjList:
            year, num = re.findall(r'\d+', item.text)
            id = re.search(r'\d{6}', str(item)).group()
            cjNum[(year, num)] = id

        # queryStr = ['111', '憲判', '2']
        url = 'https://cons.judicial.gov.tw/docdata.aspx?fid=38&id=' + str(cjNum[(queryStr[0], queryStr[2])])
        res = requests.get(url)
        par = Selector(text=res.text)
        lawList = par.css('.lawList')
        respMessage =["<" + url + ">", ]
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
                    respMessage.append('-' * 46 )
                respMessage.append(t)

        return "\n".join(respMessage)

s = CJfind(['111', '憲判', '2'])
print(s)
