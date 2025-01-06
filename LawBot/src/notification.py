# notification.py

from dotenv import load_dotenv
import os, discord
from fetch import fetch_cj_numbers, fetch_and_save_cj
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@tasks.loop(minutes = 20)
async def sched_job():
    cjNum = fetch_cj_numbers()
    BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
    CJArc = os.path.join(BASE_DIR, "res/CJArc")
    fetch_and_save_cj(cjNum, CJArc)
    for key, value in cjNum.items():
        year, num = key
        url = 'https://cons.judicial.gov.tw/docdata.aspx?fid=38&id=' + str(value)
        await channel.send(f"{year}年憲判字第{num}號已經更新摟！\n<{url}>")

@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    global channel
    channel = client.get_channel(904748448983679026)
    sched_job.start()

# Discord Bot TOKEN
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

client.run(token)