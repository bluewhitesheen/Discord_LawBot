import ast
import discord
import requests
import facebook_crawler
import time
from bs4 import BeautifulSoup


client = discord.Client()

lawDict = ast.literal_eval(open("lawDict.txt", "r", encoding='utf-8').read())
# queryDict is the expand of LawDict, O(n) prepprocess + O(lgN) each query
queryDict = {}
# lawCode stands for the default lawCode value (only edited by admin)
usage = open("usage.md", mode="r", encoding="utf-8").read()
lawCode = "A0030055"

def lawCodeFind(law: str) -> str:
    url = 'https://law.moj.gov.tw/Law/LawSearchResult.aspx?ty=ONEBAR&kw=' + law + '&sSearch='
    print(url)

    resp = requests.session()
    resp.keep_alive = False
    resp = resp.get(url, headers={'Connection':'close'})
    soup = BeautifulSoup(resp.text, 'html5lib')
    table = soup.find('table')

    # Extract the link from HTML
    # ref: https://stackoverflow.com/questions/65042243/adding-href-to-panda-read-html-df
    result = [link for link in table.find_all('td')]
    for i in range(len(result)):
        if i % 2 == 1:
            if 'label-fei' not in str(result[i]):
                pcode = result[i].find('a').get('href')[28:36]
                break
    return pcode

def lawArcFind(law: str, num: str) -> str:
    lawOld = law
    if law[-1:] == "法": law = law[:-1]
    if law[-2:] == "條例": law = law[:-2]
    url = ""
    if law.encode().isalnum():
        url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode=" + law + "&flno=" + num
    elif law in queryDict:
        url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode=" + queryDict[law] + "&flno=" + num
    # 若 url 字串仍然是空的，代表找不到
    # 此時需要將關鍵字丟入全國法規資料庫歐的搜尋，並截取最有關係的法條
    else: 
        url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode=" + lawCodeFind(lawOld) + "&flno=" + num    

    try:
        print(url)
        resp = requests.session()
        resp.keep_alive = False
        resp = resp.get(url, headers={'Connection':'close'})
        soup = BeautifulSoup(resp.text, 'html5lib')
        art = soup.select('div.law-article')[0].select('div')
        respMessage = ""
        for i in range(len(art)):
            respMessage += art[i].text + "\n"
    except Exception as e:
        print(e)
        respMessage = "抱歉，找不到餒QQ\n"
    return respMessage

#調用 event 函式庫
@client.event
#當機器人完成啟動時
async def on_ready():
    print('目前登入身份：', client.user)
    for key, value in lawDict.items():
        for i in key: queryDict[i] = value
    

@client.event
async def on_message(message):
    global lawCode
    if message.author == client.user: return
    if len(message.content) == 0: return

    print(hash(message.author), message.content)
    # 切割指令
    # 替換字元
    queryStr = message.content
    queryStr = queryStr.replace('！', '!').replace('－', '-').replace('？', '?')
    if queryStr[-1] == '條': queryStr = queryStr[:-1]
    if queryStr[-1] == '號': queryStr = queryStr[:-1]

    if queryStr[:2] == '!!': 
        global lawCode
        # Admin mode
        if hash(message.author) in (94570165215, ):
            if queryStr[-1:] == "法": queryStr = queryStr[:-1]
            if queryStr[-2:] == "條例": queryStr = queryStr[:-2]
            queryStr = queryStr[2:]
            queryStr = queryStr.split()
            if queryStr[0] == 'set': 
                for key, value in lawDict.items():
                    if queryStr[1] in key: 
                        lawCode = value
                        await message.channel.send('已將指令換成' + key[-1] + "(法/條例)!\n")

    elif queryStr[0] == '!' and queryStr[1] != '!':
        queryStr = queryStr[1:]
        queryStr = queryStr.strip()
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
            if queryStr[0] == "?": 
                await message.channel.send("```markdown\n" + usage + "```\n")
            elif queryStr[0].lower() in ("rank", "levels"): pass
            else:  
                respMessage = lawArcFind(lawCode, queryStr[0])
                await message.channel.send(respMessage)

        if len(queryStr) >= 2:
            try:
                if queryStr[0] in ("釋字", "大法官解釋", "釋", ):
                    url = "https://cons.judicial.gov.tw/docdata.aspx?fid=100&id=" + \
                        str(int(queryStr[1]) + 310181 + (queryStr[1] == '813') * (14341))

                    resp = requests.get(url)
                    soup = BeautifulSoup(resp.text, 'html5lib')

                    section = soup.find('div', class_='lawList').find_all('li')
                    respMessage = "<" + url + ">\n"
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
                                respMessage += '-' * 46 + '\n' + section[i].text.strip() + "\n"
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
                    respMsgArray = [respMessage[i:i + 2000] for i in range(0, len(respMessage), 2000)]
                    for i in respMsgArray: await message.channel.send(i)
                else:
                    respMessage = lawArcFind(queryStr[0], queryStr[1])
                    await message.channel.send(respMessage)
                    
            except Exception as e:
                print(e) 
                await message.channel.send("誒都，閣下的指令格式我解析有點問題誒QQ\n" \
                                         + "可以輸入 !? 以獲得使用說明\n")
                await message.channel.send("Error: " + str(e))
    elif queryStr[0] == '$':
        await message.channel.send("哇歐，恭喜你發現了一個新的功能！\n" \
                                    +"這個符號預計用來尋找判決，敬請期待歐~\n")

# Discord Bot TOKEN
client.run('OTM0ODQ2MDYxNTA2MzM0NzQy.Ye2BPQ.4FRER46JDoSa9V0iyPF1G4dp2oo')
