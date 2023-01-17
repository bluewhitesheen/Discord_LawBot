import os, ast, discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

#調用 event 函式庫
@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    

@client.event
async def on_message(message):
    global lawCode
    if message.author == client.user: return
    if len(message.content) == 0: return
    content = message.content
    if content.start("set "):
        cmdList = content.split()[1: ]
        print(cmdList) 
    #print(message.author.id, message.author.roles, message.content)


# Discord Bot TOKEN

if 'TOKEN_DISCUSS' in os.environ:
    client.run(os.environ['TOKEN_DISCUSS'])
else:
    token = open('../token.txt', 'r', encoding = 'utf-8').read().split('\n')
    client.run(token[2])

