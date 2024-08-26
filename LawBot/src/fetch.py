import os, ast, discord, re, requests, roman, time
from parsel import Selector
from utils import lawSoup
from tqdm import tqdm

BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
CJArc = os.path.join(BASE_DIR, "res/CJArc")

cjNum = {} 
localCJList = os.listdir(CJArc)

tmpsoup = lawSoup('https://cons.judicial.gov.tw/judcurrentNew1.aspx?fid=38').find('div', class_ = 'judgmentTabCont').find_all('li')
cjList = [item for item in tmpsoup if len(item.text) > 9]
for item in cjList:
    year, num = re.findall(r'\d+', item.text)
    id = re.search(r'\d{6}', str(item)).group()
    cjNum[(year, num)] = id


# compare cjNum dict and localCJList
for filename in localCJList:
    year, num = filename[:3], filename[3:5].lstrip('0')
    if (year, num) in cjNum: 
        del cjNum[(year, num)]
print(cjNum)

# queryStr = ['111', '憲判', '2']
for year, num in tqdm(cjNum):
    url = 'https://cons.judicial.gov.tw/docdata.aspx?fid=38&id=' + str(cjNum[(year, num)])
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
    f = open(os.path.join(CJArc, year + num.zfill(2) + ".txt"), 'w', encoding='utf-8')
    f.write("\n".join(respMessage))
    f.close()

print("finish the fetching: " + str(cjNum))