from flask import Flask, request
from bs4 import BeautifulSoup as bs
import requests
import json
import time
import os

today = time.strftime("%a").lower()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_URL = 'https://api.hphk.io/telegram'

@app.route('/{}'.format(TELEGRAM_TOKEN), methods = ['POST'])
def telegram():
    #텔레그램으로부터 요청이 들어올 경우 해당 요청을 처리하는 코드
    url = 'https://api.hphk.io/telegram/bot{}/sendMessage'.format(TELEGRAM_TOKEN) #메시지 발송 URL
    
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]
#####
    if(req["message"]["text"] == "안녕"):
        msg = "첫 만남에는 존댓말을 써야죠!" + "\n" + "바보야"
#####
    elif(req["message"]["text"] == "안녕하세요"):
        msg = "인사 잘 하신다!ㅋㅋ" + "\n" + "바보ㅋㅋㅋ"

#####
    elif(req["message"]["text"] == "환율"):
        msg = ""
        url_exc = 'https://www.x-rates.com/table/?from=USD&amount=1'
        response = requests.get(url_exc).text
        soup = bs(response,'html.parser')

        soup.select('.moduleContent .tablesorter tbody tr')[0]
        excs = []
        li = soup.select('.moduleContent .tablesorter tbody tr')
        for item in li:
            exc = {
                "nation" : list(item)[1].text,
                "value" : list(item)[3].text
            }
            excs.append(exc)
            
        for ls in excs:
            msg += ls["nation"] + " : " +ls["value"] + "\n"
#####
    elif(req["message"]["text"] == "네이버 웹툰"):
        msg = ""
        naver_url = 'https://comic.naver.com/webtoon/weekdayList.nhn?week='+today
        url_base = 'https://comic.naver.com'
        response = requests.get(naver_url).text
        soup = bs(response,'html.parser')
        
        toons = []
        li = soup.select('.img_list li')
        for item in li:
            toon = {
                "title" : item.select_one('dt a')['title'],
                "url" : url_base + item.select('dt a')[0]['href'],
            }
            toons.append(toon)
            
        for ls in toons:
            msg += ls["title"] + " : " +ls["url"] + "\n"
#####
    elif(req["message"]["text"] == "다음 웹툰"):
        msg = ""
        daum_url = 'http://webtoon.daum.net/data/pc/webtoon/list_serialized/'+today
        url_base = 'http://webtoon.daum.net/webtoon/view/'
        response = requests.get(daum_url).text
        document = json.loads(response)
        
        toons = []
        data = document['data']
        for toon in data:
            toon = {
              "title" : toon['title'],
              "url" : url_base + toon['nickname'],
            }
            toons.append(toon)
            
        for ls in toons:
            msg += ls["title"] + " : " +ls["url"] + "\n"
#####

    requests.get(url,params = {"chat_id" : chat_id, "text" : msg}) # 메시지 발송시키기
    return '', 200
    
    
@app.route('/set_webhook')
def set_webhook():
    url = TELEGRAM_URL + '/bot' + TELEGRAM_TOKEN + '/setWebhook'
    print(url)
    
    params = {
        'url' : 'https://nwongi7-nwongi7.c9users.io/{}'.format(TELEGRAM_TOKEN)
    }
    
    response = requests.get(url, params = params).text
    return response