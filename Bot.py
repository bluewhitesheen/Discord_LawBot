import roman
import discord
import requests
from bs4 import BeautifulSoup
client = discord.Client()

lawDict = {
    #行政法
    ("憲", "中華民國憲"): "A0000001",
    ("憲增", "憲法增修", "憲法增修條文"): "A0000002",
    ("行程", "行政程序"): "A0030055",
    ("行執", "行政執行"): "A0030023",
    ("行罰", "行政罰"): "A0030210",
    ("行訴", "行政訴訟"): "A0030154",
    ("憲訴", "憲法訴訟"): "A0030159",
    ("願", "訴願"): "A0030020",
    ("國賠", "國家賠償"): "I0020004",
    ("地制", "地方制度"): "A0040003",
    ("行政法人"): "A0010102",

    # 民法（原諒我將法組放在這邊，我暫時沒什麼頭緒）
    ("民"): "B0000001",
    ("民訴", "民事訴訟"): "B0010001",
    ("家事", "家事事件"): "B0010048",
    ("法組", "法院組織"): "A0010053",
    ("強制", "強制執行"): "B0010004",

    #刑法
    ("刑", "中華民國刑"): "C0000001",
    ("刑訴", "刑事訴訟"): "C0010001",
    ("貪汙", "貪治", "貪汙治罪"): "C0000007",
    ("妥速審判", "刑事妥速審判"): "C0010027",

    # 商法
    ("公", "公司"): "C0010001",
    ("保", "保險"): "G0390002",
    ("證", "證交", "證券交易"): "G0400001",
    ("企併", "企業併購"): "J0080041",
    ("銀行"): "G0380001",
    ("票據"): "G0380028",
    ("有限合夥"): "J0080051",

    # 選試：智財法
    ("著", "著作", "著作權"): "J0070017",
    ("商標"): "J0070001",
    ("專利"): "J0070007",

    # 選試：財稅法
    ("財劃", "財政收支劃分"): "G0320015",
    ("納保", "納稅者權利保護"): "G0340142",
    ("稅稽", "稅捐稽徵"): "G0340001",
    ("所", "所得稅"): "G0340003",
    ("遺贈", "遺產及贈與稅"): "G0340072",
    ("營業", "營業稅", "加值型及非加值型營業稅"): "G0340080",

    # 選試：勞動社會法
    ("勞", "勞基", "勞動基準"): "N0030001",
    ("勞動基準法施行細則"): "N0030002",
    ("勞資爭議處理"): "N0020007",
    ("勞保", "勞工保險"): "N0050001",

    # 選試：海商法
    ("海商"): "K0070002",

    # 自己想加或別人許願的法條OuO
    ("公交", "公平交易"): "J0150002",
    ("土", "土地"): "D0060001",
    ("消保", "消費者保護"): "J0170001",
    ("通保", "通監", "通訊保障及監察"): "K0060044",
    ("國民法官"): "A0030320",
    ("公寓", "公寓大廈", "公寓大廈管理"): "D0070118",
}

#調用 event 函式庫


@client.event
#當機器人完成啟動時
async def on_ready():
    print('目前登入身份：', client.user)


@client.event
#當有訊息時
async def on_message(message):
    #排除自己的訊息，避免陷入無限循環
    if message.author == client.user:
        return
    if len(message.content) == 0:
        return

    queryStr = message.content
    queryStr = queryStr.replace('！', '!')
    queryStr = queryStr.replace('－', '-')

    if queryStr[0] == '!':
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
            if queryStr[0] in ("h", "help"):
                helpMessage = "使用方式: ! + 法規名稱（或釋字） + 條號，例如：!刑309, !釋509, ！公司法189\n目前支援的法條：\n"
                await message.channel.send(helpMessage)
                for key in lawDict.keys():
                    await message.channel.send(key + "\n")

        if len(queryStr) >= 2:
            try:
                if queryStr[0] in ("釋字", "大法官解釋", "釋"):
                    urlDisplay = "<https://cons.judicial.gov.tw/docdata.aspx?fid=100&id=" + \
                        str(int(queryStr[1]) + 310181 +
                            (queryStr[1] == '813') * (14341)) + ">"
                    url = "https://law.moj.gov.tw/LawClass/ExContent.aspx?media=print&ty=C&CC=D&CNO=" + \
                        queryStr[1]
                    await message.channel.send(urlDisplay)
                    resp = requests.get(url)
                    soup = BeautifulSoup(resp.text, 'lxml')
                    # 前面的瑣碎資訊
                    art = soup.select('div.col-td')
                    for i in range(len(art)):
                        if i == 1 or i == 2:
                            respMessage = art[i].text.strip()
                            await message.channel.send(respMessage)
                    # 解釋文
                    art = soup.select('div.font-s')
                    for i in art:
                        #respMessage = i.text.strip()
                        respMessage = i.text
                        await message.channel.send(respMessage)
                else:
                    if queryStr[0][-1:] == "法":
                        queryStr[0] = queryStr[0][:-1]
                    if queryStr[0][-2:] == "條例":
                        queryStr[0] = queryStr[0][:-2]

                    for key, value in lawDict.items():
                        if queryStr[0] in key:
                            url = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?PCode=" + \
                                value + "&flno=" + queryStr[1]
                            print(url)
                            resp = requests.get(url)
                            soup = BeautifulSoup(resp.text, 'lxml')
                            art = soup.select(
                                'div.law-article')[0].select('div')
                            print(art)
                            respMessage = ""
                            for i in range(len(art)):
                                respMessage += art[i].text + "\n"
                            await message.channel.send(respMessage)
                            break
            except:
                await message.channel.send("誒都，閣下的指令格式我解析有點問題誒QQ")
# Discord Bot TOKEN
client.run('OTM0ODQ2MDYxNTA2MzM0NzQy.Ye2BPQ.4FRER46JDoSa9V0iyPF1G4dp2oo')
