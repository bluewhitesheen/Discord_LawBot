import re, os, ast, roman, discord, requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
lawDictDir = os.path.join(BASE_DIR, "lawDict.txt")
lawDict = ast.literal_eval(open(lawDictDir, "r", encoding='utf-8').read())
usageDir = os.path.join(BASE_DIR, "usage.md")
usage = open(usageDir, mode="r", encoding="utf-8").read()

queryDict = {}
# lawCode stands for the default lawCode value
lawCode = "A0030055"

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
    if queryList[0][-1:] == "法": queryList[0] = queryList[0][:-1]
    if queryList[0][-2:] == "條例": queryList[0] = queryList[0][:-2]
    return queryList

def JudicalJudgmenetStr(queryStr: str):
    queryList = []
    match_result = re.match('([0-9]+)([\u4e00-\u9fff]+)([0-9]+)', queryStr)
    if match_result:
        queryList = list(match_result.groups())
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
    try:
        result = [link for link in table.find_all('td')][1::2]
        result_pair = []
        for i in range(len(result)):
            tmptag = result[i].find('a')
            tmpcode = tmptag.get('href')[28:36]
            tmpname = tmptag.text
            result_pair.append((tmpname, tmpcode))
        result_pair = sorted(result_pair, key = lambda p: len(p[0]))
        print(result_pair)
        pcode = result_pair[0][1]
        return pcode
    except: 
        return 'Z9999999'

def lawArcFind(queryList):
    if queryList[0] == '': queryList[0] = lawCode
    url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode="
    if queryList[0].encode().isalnum(): pass
    elif queryList[0] in queryDict:
        queryList[0] = queryDict[queryList[0]]
    # If lawname is not in Lawdict
    # then find the lawname from law.moj.gov.tw, and capture the most relavant law in the result
    else: 
        queryList[0] = lawCodeFind(queryList[0])
        if queryList[0] == 'Z9999999': 
            return 'Z9999999'
            

    if queryList[1].isnumeric() and int(queryList[1]) == 0:
        loc = url.find('/LawSingle.aspx?')
        url = url[:loc] + '/LawAll.aspx?pcode=' + queryList[0]
        return url
    else:
        url += queryList[0] + "&flno=" + queryList[1]

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
    except: pass
    return respMessage

def JIArcFind(JInum: int):
    f = open("JIArc/" + str(JInum) + ".txt", mode="r", encoding="utf-8")
    respMessage = f.read()
    f.close()
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
        if section[i].text.strip() == '理由': break
        if section[i].text.strip() == '主文': flag = 1
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

    queryStr = message.content
    if len(queryStr) > 3 and queryStr in 'nuguseyo': 
        await message.channel.send('台\n大\n法\n律\n系\n')
        return
    queryStr = queryStr.replace('！', '!').replace('－', '-').replace('？', '?').replace('§', '').replace(' ', '')
    if queryStr[-1] == '條': queryStr = queryStr[:-1]
    if queryStr[-1] == '號': queryStr = queryStr[:-1]
    if queryStr.startswith('set'): 
        # Admin mode
        roles = [r.name for r in message.author.roles]
        if "管理員" in roles or "討論活動負責人" in roles or message.author.id in [396656022241935362, ]:
            queryStr = queryStr.replace("set", "set ")
            lawName = queryStr.split()[1]
            if lawName[-1:] == "法": lawName = lawName[:-1]
            if lawName[-2:] == "條例": lawName = lawName[:-2]
            if lawName in queryDict:
                lawCode = queryDict[lawName]
                await message.channel.send("預設指令變更摟!\n")

    else: 
        flag, respMessage = 0, ""
        if queryStr[0] == '$':
            queryStr = JudicalJudgmenetStr(queryStr[1:])
            try: respMessage = CJfind(queryStr)
            except: pass
        else:
            if queryStr[0] == '!':
                flag = 1
                queryStr = queryStr[1:]
            queryStr = queryStrPreprocess(queryStr)
            if queryStr == [] or queryStr[1] == '': return 
            print(queryStr)
            try:
                respMessage = ""
                if queryStr[0] == "?": 
                    respMessage = "```markdown\n" + usage + "```\n"
                elif queryStr[0] in ("釋字", "大法官解釋", "釋", ):
                    respMessage = JIArcFind(queryStr[1])
                elif flag or queryStr[0] in queryDict:
                    respMessage = lawArcFind(queryStr)
            except Exception as e:
                await message.channel.send("誒都，閣下的指令格式我解析有點問題誒QQ\n" + "可以輸入 !? 以獲得使用說明\n") 
                print(e)
        if  respMessage == 'Z9999999':
            await message.channel.send('誒都，找不到閣下的法條誒QQ\n搜尋冷門法條時，建議不要打法條簡稱喔！\n')
            return
        if len(respMessage): 
            respMessage = splitMsg(respMessage)
            for i in respMessage: await message.channel.send(i)
        

# Discord Bot TOKEN

if 'TOKEN_LAWBOT' in os.environ:
    client.run(os.environ['TOKEN_LAWBOT'])
else:
    token = open('../token.txt', 'r', encoding = 'utf-8').read().split('\n')
    client.run(token[0])

