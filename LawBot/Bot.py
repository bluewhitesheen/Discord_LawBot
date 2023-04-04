import re, os, ast, roman, discord, requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

lawDict = ast.literal_eval(open("lawDict.txt", "r", encoding='utf-8').read())
# queryDict is the expand of LawDict, O(n) prepprocess + O(lgN) each query
queryDict = {}
# lawCode stands for the default lawCode value (only edited by admin)
usage = open("usage.md", mode="r", encoding="utf-8").read()
lawCode = "A0030055"

def queryStrPreprocess(queryStr: str):
    match_result = re.match('([\u4e00-\u9fff\\?]*)([0-9-]*)([IVX]*)', queryStr, re.I)
    if type(match_result.groups()) != None: 
        queryList = list(match_result.groups())
        if queryList[-1] == '': queryList = queryList[:-1]
    try: 
        queryList[-1] = roman.fromRoman(queryList[-1])
    except: pass
    if queryList[0][-1:] == "法": queryList[0] = queryList[0][:-1]
    if queryList[0][-2:] == "條例": queryList[0] = queryList[0][:-2]
    return queryList

def JudicalJudgmenetStr(queryStr: str):
    match_result = re.match('([0-9]+)([\u4e00-\u9fff]+)([0-9]+)', queryStr)
    if type(match_result.groups()) != None:
        queryList = list(match_result.groups())
    return queryList


def splitMsg(respMessage: str):
    result = []
    L = 0
    while L < len(respMessage) - 1:
        R = respMessage.rfind('\n', L, L + 2000)
        result.append(respMessage[L: R+1])
        L = R
    return result


def lawSoup(url: str):
    resp = requests.session()
    resp.keep_alive = False
    resp = resp.get(url, headers={'Connection': 'close'},  verify=False)
    soup = BeautifulSoup(resp.text, "lxml")
    return soup

def lawCodeFind(law: str) -> str:
    url = 'https://law.moj.gov.tw/Law/LawSearchResult.aspx?ty=ONEBAR&kw=' + law + '&sSearch='
    print(url)

    soup = lawSoup(url)
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

# Due to law "paragraph" lvl finding, changing the parameters "str law, num" to "list queryStr"
def lawArcFind(queryList):
    lawOld = queryList[0]
    url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode="
    if queryList[0].encode().isalnum():
        url += queryList[0] + "&flno=" + queryList[1]
    elif queryList[0] in queryDict:
        url += queryDict[queryList[0]] + "&flno=" + queryList[1]
    # If lawname is not in Lawdict
    # then find the lawname from law.moj.gov.tw, and capture the most relavant law in the result
    else: 
        url += lawCodeFind(lawOld) + "&flno=" + queryList[1]
    respMessage = ""
    try:
        print(url)
        soup = lawSoup(url)
        art = soup.select('div.law-article')[0].select('div')
        if len(queryList) == 2:
            for i in range(len(art)):
                respMessage += art[i].text + "\n"
        elif len(queryList) == 3:
            arttmp = soup.select('div.law-article')[0].select('div.line-0000')[queryList[2] - 1]
            arttmp = art.index(arttmp)
            while True:
                respMessage += art[arttmp].text + "\n"
                arttmp += 1
                if "line-0000" in str(art[arttmp]): break
            print(respMessage)
    except Exception as e: pass
    return respMessage

def JIArcFind(JInum: int):
    url = "https://cons.judicial.gov.tw/docdata.aspx?fid=100&id=" + \
        str(int(JInum) + 310181 + (JInum == '813') * (14341))

    soup = lawSoup(url)
    section = soup.find('div', class_='lawList').find_all('li')
    respMessage = "<" + url + ">\n"
    flag = 1
    for i in range(len(section)):
        # 過濾不想要的章節
        if section[i].text in ("解釋公布院令", "解釋更正院令", "理由書"): flag = 0
        elif section[i].text in ("解釋字號", "解釋爭點", "解釋文"): flag = 1
        if section[i].text == "意見書": break
        if flag == 0: continue

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
    return respMessage

# Constitutional Judgement finding function
def CJfind(queryStr):
    cjNum = {} 
    tmpsoup = lawSoup('https://cons.judicial.gov.tw/judcurrentNew1.aspx?fid=38').find('div', class_ = 'judgmentTabCont').find_all('li')
    tmpsoup = [i for i in tmpsoup if 'docdata.aspx?' in str(i)]
    for i in tmpsoup: 
        s = str(i).replace("&amp;", '&')
        try: 
            _, id, yr, num = re.findall('\d+', s)
            cjNum[(yr, num)] = id
        except: pass
    # queryStr = ['111', '憲判', '2']
    url = 'https://cons.judicial.gov.tw/docdata.aspx?fid=38&id=' + str(cjNum[(queryStr[0], queryStr[2])])
    soup = lawSoup(url)
    section = soup.find('div', class_='lawList').find_all('li')

    respMessage = ["<" + url + ">\n"]
    flag = 0

    for i in range(len(section)):
        if section[i].text.strip() == '理由':
            break
        if section[i].text.strip() == '主文':
            flag = 1
        if section[i].text.strip() in ('判決字號', '原分案號', '判決日期', '聲請人', '案由', '主文'):
            respMessage.append('-' * 46 + '\n')
        if flag == 0:
            resstr = section[i].text.strip()
            if resstr + '\n' not in respMessage:
                respMessage.append(resstr + '\n')
        else:
            for s in section[i].select('label'):
                s.extract()
            resstr = section[i].text.strip()
            respMessage.append(resstr + '\n')
    
    respMessage = "".join(respMessage)
    return respMessage

#調用 event 函式庫
@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    for key, value in lawDict.items():
        for i in key: queryDict[i] = value
    

@client.event
async def on_message(message):
    global lawCode
    if message.author == client.user: return
    if len(message.content) == 0: return
    #print(message.author.id, message.author.roles, message.content)

    # 切割指令
    # 替換字元
    queryStr = message.content
    queryStr = queryStr.replace('！', '!').replace('－', '-').replace('？', '?').replace('§', '').replace(' ', '')
    if queryStr[-1] == '條': queryStr = queryStr[:-1]
    if queryStr[-1] == '號': queryStr = queryStr[:-1]

    if queryStr[:2] == '!!': 
        # Admin mode
        roles = [r.name for r in message.author.roles]
        if "管理員" in roles or "討論活動負責人" in roles or message.author.id in [396656022241935362, ]:
            queryStr = queryStr.replace("set", "set ")
            if queryStr[-1:] == "法": queryStr = queryStr[:-1]
            if queryStr[-2:] == "條例": queryStr = queryStr[:-2]
            queryStr = queryStr[2:]
            queryStr = queryStr.split()
            print(queryStr)
            if queryStr[0].lower() == 'set': 
                for key, value in lawDict.items():
                    if queryStr[1] in key: 
                        lawCode = value
                        await message.channel.send('已將指令換成' + key[-1] + "(法/條例)!\n")

    elif queryStr[0] == '!':
        try:
            queryStr = queryStrPreprocess(queryStr[1:])
            respMessage = ""
            if queryStr[0] == "?": 
                respMessage = "```markdown\n" + usage + "```\n"
            elif queryStr[0] == "":
                queryStr[0] = lawCode
                respMessage = lawArcFind(queryStr)
            elif queryStr[0] in ("釋字", "大法官解釋", "釋", ):
                respMessage = JIArcFind(queryStr[1])
            elif len(queryStr[0]) != 0:
                respMessage = lawArcFind(queryStr)
            if len(respMessage):
                respMessage = splitMsg(respMessage)
                for i in respMessage: await message.channel.send(i)
        except Exception as e:
            print(e) 
            await message.channel.send("誒都，閣下的指令格式我解析有點問題誒QQ\n" \
                                        + "可以輸入 !? 以獲得使用說明\n")
            await message.channel.send("Error: " + str(e))

    elif queryStr[0] == '$':
        queryStr = JudicalJudgmenetStr(queryStr[1:])
        try:
            respMessage = CJfind(queryStr)
            respMessage = splitMsg(respMessage)
            for i in respMessage: await message.channel.send(i)
        except Exception as e:
            print(e)
    else: 
        try:
            queryStr = queryStrPreprocess(queryStr)
            if queryStr[0] in ("釋字", "大法官解釋", "釋", ):
                respMessage = JIArcFind(queryStr[1])
            else:
                if queryStr[0] in queryDict:
                    respMessage = lawArcFind(queryStr)
            if len(respMessage):
                respMessage = splitMsg(respMessage)
                for i in respMessage: await message.channel.send(i)
        except: pass


# Discord Bot TOKEN

if 'TOKEN_LAWBOT' in os.environ:
    client.run(os.environ['TOKEN_LAWBOT'])
else:
    token = open('../token.txt', 'r', encoding = 'utf-8').read().split('\n')
    client.run(token[0])

