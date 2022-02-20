import discord
import requests
from bs4 import BeautifulSoup
client = discord.Client()

lawDict = {
    #行政法
    ("憲", "中華民國憲", ): "A0000001",
    ("憲增", "憲法增修", "憲法增修條文", ): "A0000002",
    ("行", "行程", "行政程序", ): "A0030055",
    ("行執", "行政執行", ): "A0030023",
    ("行罰", "行政罰", ): "A0030210",
    ("行訴", "行政訴訟", ): "A0030154",
    ("憲訴", "憲法訴訟", ): "A0030159",
    ("願", "訴願", ): "A0030020",
    ("國賠", "國家賠償", ): "I0020004",
    ("地制", "地方制度", ): "A0040003",
    ("行政法人", ): "A0010102",
    ("海商", ): "K0070002",
    ("通保", "通監", "通訊保障及監察", ): "K0060044",
    ("公寓", "公寓大廈", "公寓大廈管理", ): "D0070118",

    # 民法（原諒我將法組放在這邊，我暫時沒什麼頭緒）
    ("民", ): "B0000001",
    ("民訴", "民事訴訟", ): "B0010001",
    ("家事", "家事事件", ): "B0010048",
    ("法組", "法院組織", ): "A0010053",
    ("強制", "強制執行", "強執"): "B0010004",
    ("土", "土地", ): "D0060001",

    #刑法
    ("刑", "中華民國刑", ): "C0000001",
    ("刑訴", "刑事訴訟", ): "C0010001",
    ("貪汙", "貪治", "貪汙治罪", ): "C0000007",
    ("妥速審判", "刑事妥速審判", ): "C0010027",

    # 商法
    ("公", "公司", ): "J0080001",
    ("保", "保險", ): "G0390002",
    ("證", "證交", "證券交易", ): "G0400001",
    ("企併", "企業併購", ): "J0080041",
    ("銀", "銀行", ): "G0380001",
    ("票", "票據", ): "G0380028",
    ("有限合夥", ): "J0080051",
    ("著", "著作", "著作權", ): "J0070017",
    ("商標", ): "J0070001",
    ("專利", ): "J0070007",
    ("公交", "公平交易", ): "J0150002",
    ("消保", "消費者保護", ): "J0170001",

    # 選試：財稅法
    ("財劃", "財政收支劃分", ): "G0320015",
    ("納保", "納稅者權利保護", ): "G0340142",
    ("稅稽", "稅捐稽徵", ): "G0340001",
    ("所", "所得稅", ): "G0340003",
    ("遺贈", "遺產及贈與稅", ): "G0340072",
    ("營業", "營業稅", "加值型及非加值型營業稅", ): "G0340080",
    ("查準", "營所查準", "營利事業所得稅查核準則",): "G0340051",

    # 選試：勞動社會法
    ("勞", "勞基", "勞動基準", ): "N0030001",
    ("勞資爭議處理", ): "N0020007",
    ("勞保", "勞工保險", ): "N0050001",
}

# Query Dict is the expand of LawDict, O(n) prepprocess + O(lgN) each query
QueryDict = {}
# lawCode stands for the default lawCode value
lawCode = "A0030055"
# usage stands for the usage of the bot
usage = open("usage.md", mode="r", encoding="utf-8").read()


def lawArcFind(law: str, num: str) -> str:
    if law[-1:] == "法": law = law[:-1]
    if law[-2:] == "條例": law = law[:-2]
    url = ""
    if law.encode().isalnum():
        url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode=" + law + "&flno=" + num
    else:
        for key, value in lawDict.items():
            if law in key:
                url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode=" + value + "&flno=" + num
                break
    
    # 若 url 字串仍然是空的，代表找不到
    # 此時需要將關鍵字丟入全國法規資料庫歐的搜尋，並截取最有關係的法條
    if url == "": 
        kw = law
        urlSearch = 'https://law.moj.gov.tw/Law/LawSearchResult.aspx?ty=ONEBAR&kw=' + kw + '&sSearch='
        respSearch = requests.get(urlSearch)
        soup = BeautifulSoup(respSearch.text, 'html5lib')
        table = soup.find('table')

        # Extract the link from HTML
        # ref: https://stackoverflow.com/questions/65042243/adding-href-to-panda-read-html-df
        result = [link for link in table.find_all('td')]
        for i in range(len(result)):
            if i % 2 == 1:
                if 'label-fei' not in str(result[i]):
                    pcode = result[i].find('a').get('href')[28:36]
                    break
        return lawArcFind(pcode, num)

    try:
        print(url)
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html5lib')
        art = soup.select('div.law-article')[0].select('div')
        respMessage = ""
        for i in range(len(art)):
            respMessage += art[i].text + "\n"
    except Exception as e:
        print(e)
        respMessage = ""
    return respMessage

#調用 event 函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
    print('目前登入身份：', client.user)
    for key, value in lawDict.items():
        for i in key: QueryDict[i] = value
    

@client.event
async def on_message(message):
    if message.author == client.user: return
    if len(message.content) == 0: return

    # 切割指令
    # 替換字元
    queryStr = message.content
    queryStr = queryStr.replace('！', '!')
    queryStr = queryStr.replace('－', '-')
    queryStr = queryStr.replace('？', '?')
    if queryStr[-1] == '條': queryStr = queryStr[:-1]
    if queryStr[-1] == '號': queryStr = queryStr[:-1]

    if queryStr[0] == '!' and queryStr[1] != '!':
        queryStr = queryStr[1:]
        # 將指令拆成中文跟法條
        for i in range(len(queryStr)):
            if queryStr[i].isascii():
                queryStr = queryStr[:i] + ' ' + queryStr[i:]
                break
        # 將指令拆成法條跟項號
        for i in range(len(queryStr)):
            if queryStr[i].encode('utf-8').isalpha():
                queryStr = queryStr[:i] + ' ' + queryStr[i:]
                break
        print(queryStr)
        queryStr = queryStr.split()

        if len(queryStr) == 1:
            if queryStr[0] in ("?", "使用說明", "說明", "使用", "使"): 
                respMessage = "```markdown\n" + usage + "```\n"
                await message.channel.send(respMessage)
            elif queryStr[0].lower() in ("rank", "levels"): pass
            else: 
                global lawCode
                respMessage = lawArcFind(lawCode, queryStr[0])
                if len(respMessage) == 0:
                    respMessage = "抱歉，找不到餒QQ\n"
                await message.channel.send(respMessage)

        if len(queryStr) >= 2:
            try:
                if queryStr[0] in ("釋字", "大法官解釋", "釋", ):
                    url = "https://cons.judicial.gov.tw/docdata.aspx?fid=100&id=" + \
                        str(int(queryStr[1]) + 310181 + (queryStr[1] == '813') * (14341))
                    await message.channel.send("<" + url + ">")

                    resp = requests.get(url)
                    soup = BeautifulSoup(resp.text, 'html5lib')

                    section = soup.find('div', class_='lawList').find_all('li')
                    respMessage = ''
                    flag = 1
                    for i in range(len(section)):
                        # 過濾不想要的章節
                        if section[i].text in ("解釋公布院令", "解釋更正院令", "理由書"): flag = 0
                        elif section[i].text in ("解釋字號", "解釋爭點", "解釋文"): flag = 1
                        if section[i].text == "意見書": break
                        if flag == 0:  continue

                        # 輸出過濾後的部分
                        if len(section[i].find_all('li')) > 0:
                            continue
                        else:
                            # 拆分 tag 是 title 還是 text
                            if 'class="title"' in str(section[i]):
                                respMessage += '----------------------------------------------\n' + section[i].text.strip() + "\n"
                            else:
                                paragraph = section[i].find('pre')
                                # 因為解釋文跟理由書的架構為 li > (label -> pre)，我們只要 pre 的部分
                                # pre 只會有一個，所以直接用 find()
                                if paragraph != None:
                                    tmp = paragraph.text.strip()
                                    if tmp.find('大法官會議主席') != -1: break
                                    else: respMessage += tmp + "\n"
                                else:
                                    respMessage += section[i].text.strip() + "\n"
                    await message.channel.send(respMessage)
                else:
                    respMessage = lawArcFind(queryStr[0], queryStr[1])
                    if len(respMessage) == 0: respMessage = "抱歉，找不到餒QQ\n"
                    await message.channel.send(respMessage)
                    
            except Exception as e:
                print(e) 
                await message.channel.send("誒都，閣下的指令格式我解析有點問題誒QQ\n" \
                                         + "可以輸入 !? 以獲得使用說明\n")
    if queryStr[:2] == '!!': 
        # Admin mode
        if hash(message.author) == 94570165215:
            queryStr = queryStr[2:]
            queryStr = queryStr.split()
            if queryStr[0] == 'set': 
                for key, value in lawDict.items():
                    if queryStr[1] in key: 
                        lawCode = value
                        await message.channel.send('已將指令換成' + key[-1] + "(法/條例)!\n")

# Discord Bot TOKEN
client.run('OTM0ODQ2MDYxNTA2MzM0NzQy.Ye2BPQ.4FRER46JDoSa9V0iyPF1G4dp2oo')
