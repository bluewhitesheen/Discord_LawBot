from apscheduler.schedulers.blocking import BlockingScheduler
import requests
sched = BlockingScheduler()

@sched.scheduled_job('cron', minute = '*/5')
def sched_job():
    url = 'https://discord-law-bot.herokuapp.com/'
    conn = requests.get(url)

print('clock.py is open!')
sched.start()
