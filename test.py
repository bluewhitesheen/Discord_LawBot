import requests
from parsel import Selector
import re

res = requests.get('https://cons.judicial.gov.tw/docdata.aspx?fid=38&id=309998')
par = Selector(text=res.text)
lawList = par.css('.lawList')
newLawList = []
pureNumber = re.compile('^\d*$')
for item in lawList:
    text = item.xpath('.//text()').getall()
    for t in text:
        t = t.strip()
        if len(t) == 0 or pureNumber.match(t) is not None:
            continue
        newLawList.append(t)

for i in range(len(newLawList)):
    if newLawList[i] == '理由':
        break
    print(newLawList[i])    