from apscheduler.schedulers.blocking import BlockingScheduler
import requests

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=3)
def scheduled_job():
    url = "https://discord-law-bot.herokuapp.com/"
    conn = requests.get(url)
    for key, value in conn.getheaders():
        print(key, value)
sched.start()
