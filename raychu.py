import time
import datetime
import discord
import facebook_crawler
from discord.ext import tasks

def getNewestPost():  
    today = datetime.datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
    oneday = datetime.timedelta(days = 1)
    yesterday = today - oneday
    pageurl= 'https://www.facebook.com/raychu.eclat12'
    pd = facebook_crawler.Crawl_PagePosts(pageurl=pageurl, until_date=yesterday)
    print(pd)
    result = pd
    result = result[["TIME", "MESSAGE", "LINK", "POSTID"]].iloc[0]
    result = list(result)
    result[2:4] = [result[2] + "posts/" + result[3]]
    return result

client = discord.Client()
channel = {}

@tasks.loop(minutes = 2)
async def sched_job():
    global channel
    messages = await channel.history(limit=10).flatten()
    message = [msg for msg in messages if msg.author.id ==
               955708093818351697][0]
    # for msg in messages:
    #     print(msg, msg.content)
    getPostMsg = getNewestPost()
    getPostMsg = "雷丘律師有新貼文摟！\n" + "-" * 46 + "\n" \
        + getPostMsg[1] + "\n" \
        + getPostMsg[2] + "\n" \
        + "Timestamp: " + getPostMsg[0]
    if message.content != getPostMsg:
        await channel.send(getPostMsg)

#調用 event 函式庫
@client.event
#當機器人完成啟動時
async def on_ready(): 
    print('目前登入身份：', client.user)
    global channel
    channel = client.get_channel(949311884476186655)
    sched_job.start()

client.run('OTU1NzA4MDkzODE4MzUxNjk3.YjlmhQ.E9Vc5Zjedf3ObFF_aSq37McrK3Y')


