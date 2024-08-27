import threading
import os

def run_bot():
    os.system('python LawBot/src/bot.py')

def run_notification():
    os.system('python LawBot/src/notification.py')

# 創建兩個線程
bot_thread = threading.Thread(target=run_bot)
notification_thread = threading.Thread(target=run_notification)

# 啟動線程
bot_thread.start()
notification_thread.start()

# 等待線程結束（可選）
bot_thread.join()
notification_thread.join()
