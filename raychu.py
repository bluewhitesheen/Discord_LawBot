import os
import time
import datetime
import discord
import facebook_crawler
from discord.ext import tasks
from dotenv import load_dotenv

def getNewestPost():  
    today = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
    oneday = datetime.timedelta(days = 1)
    yesterday = today - oneday
    yesterday = str(yesterday)
    pageurl= 'https://www.facebook.com/raychu.eclat12'
    pd = facebook_crawler.Crawl_PagePosts(pageurl=pageurl, until_date=yesterday)
    result = pd
    result = result[["TIME", "MESSAGE", "LINK", "POSTID"]].iloc[0]
    result = list(result)
    result[2:4] = [result[2] + "posts/" + result[3]]
    if len(result[1]) == 0: result[1] = "雷丘律師僅發了一張圖片，請點擊下面的網址OuOb!"
    return result

client = discord.Client()
channel = {}

@tasks.loop(minutes = 30)
async def sched_job():
    try:
        global channel
        messages = await channel.history(limit=10).flatten()
        message = [msg for msg in messages if msg.author.id ==
                955708093818351697][0]
        # for msg in messages:
        #     print(msg, msg.content)
        getPost = getNewestPost()
        getPostMsg = "雷丘律師有新貼文摟！\n" + "-" * 46 + "\n" \
            + getPost[1] + "\n<" \
            + getPost[2] + ">\n" \
            + "Timestamp: " + getPost[0]
        dcTimeStamp = " ".join(message.content.split('\n')[-1].split()[-2: ])
        if message.content != getPostMsg and dcTimeStamp < getPost[0]:
            await channel.send(getPostMsg)
    except Exception as e:
        curTime = time.strftime("%Y-%m-%d %H:%M:%S")
        print(curTime, e)   

#調用 event 函式庫
@client.event
#當機器人完成啟動時
async def on_ready(): 
    print('目前登入身份：', client.user)
    global channel
    channel = client.get_channel(949311884476186655)
    sched_job.start()

# Discord Bot TOKEN
load_dotenv()
token = os.getenv("RAYCHU_TOKEN")

client.run(token)

