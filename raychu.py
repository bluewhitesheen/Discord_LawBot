import facebook_crawler
import time

def getNewestPost():  
    today = time.strftime("%Y-%m-%d") 
    pageurl= 'https://www.facebook.com/raychu.eclat12'
    pd = facebook_crawler.Crawl_PagePosts(pageurl=pageurl, until_date=today)
    result = pd
    result = result[["TIME", "MESSAGE", "LINK", "POSTID"]].iloc[0]
    result = list(result)
    result[2:4] = [result[2] + "/pages/" + result[3]]
    return result

