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

###############################################################################
CAFE_LIST = {
    '전체' : -1,
    '부천점' : 15,
    '안양점' : 13,
    '대구동성로2호점' : 14,
    '대구동성로점' : 9,
    '궁동직영점' : 1,
    '은행직영점' : 2,
    '부산서면점' : 19,
    '홍대상수점' : 20,
    '강남점' : 16,
    '건대점' : 10,
    '홍대점' : 11,
    '신촌점' : 6,
    '잠실점' : 21,
    '부평점' : 17,
    '익산점' : 12,
    '전주고사점' : 8,
    '천안신부점' : 18,
    '천안점' : 3,
    '천안두정점' : 7,
    '청주점' : 4
}

def master_key_info(cd):
    url = "http://www.master-key.co.kr/booking/booking_list_new"
    params = {
        "date" : time.strftime('%Y-%m-%d'),
        "store" : cd,
        "room" : ""
    }
    
    response = requests.post(url, params).text
    documents = bs(response, 'html.parser')
    ul = documents.select('.reserve .escape_view')
    
    theme_list = []
    for li in ul:
        title = li.select('p')[0].text
        info = ''
        for col in li.select('.col'):
            info = info + '{} - {}\n'.format(col.select_one('.time').text, col.select_one('.state').text)
        theme = {
            'title' : title,
            'info' : info
        }
        theme_list.append(theme)
    return(theme_list)
    
def master_key_list():
    url = 'http://www.master-key.co.kr/home/office'
    
    response = requests.get(url).text
    soup = bs(response, 'html.parser')
    lis = soup.select('.escape_list .escape_view')
    
    cafe_list = []
    url_base = 'http://www.master-key.co.kr'
    for li in lis:
        title = li.select_one('p').text #부천점NEW
        if(title.endswith('NEW')):
            title = title[:-3] #부천점
        address = li.select('dd')[0].text.strip() #경기도 부천시 (주소)
        tel = li.select('dd')[1].text #전화번호
        link = li.select_one('a')['href'] #예약url일부
        
        cafe = {
            'title' : title,
            'tel' : tel,
            'address' : address,
            'link' : '{}{}'.format(url_base,link)
        }
        
        cafe_list.append(cafe)
    return(cafe_list)

###############################################################################
def get_total_info():
    url = 'http://www.seoul-escape.com/reservation/change_date/'
    params = {
        "current_date" : '2018/12/21'
    }

    response = requests.get(url, params = params).text
    document = json.loads(response)

    cafe_code = {
        "강남1호점" : 3,
        "홍대1호점" : 1,
        "부산 서면점" : 5,
        "인천 부평점" : 4,
        "강남2호점" : 11,
        "홍대2호점" : 10,
    }

    total = {}
    game_room_list = document['gameRoomList']

    #기본 틀 잡기
    for cafe in cafe_code:
        total[cafe] = []
        for room in game_room_list:
            if(cafe_code[cafe] == room["branch_id"]):
                total[cafe].append({'title' : room['room_name'], "info":[]})

    #앞에서 잡은 틀에 데이터 집어넣기
    book_list = document['bookList']
    for cafe in total:
        for book in book_list:
            if(cafe == book["branch"]):
                for theme in total[cafe]:
                    if(theme['title'] == book['room']):
                        if(book['booked']):
                            booked = "예약완료"
                        else:
                            booked = "예약가능"
                        theme['info'].append("{} - {}".format(book['hour'],booked))
    return(total)
    
def seoul_escape_list():
    total = get_total_info()
    return total.keys()

def seoul_escape_info(cd):
    total = get_total_info()
    cafe = total[cd]
    tmp = []
    for theme in cafe:
        tmp.append("{}\n {}".format(theme['title'],'\n'.join(theme['info'])))
    return(tmp)

###############################################################################
@app.route('/{}'.format(TELEGRAM_TOKEN), methods = ['POST'])
def telegram():
    #텔레그램으로부터 요청이 들어올 경우 해당 요청을 처리하는 코드
    url = 'https://api.hphk.io/telegram/bot{}/sendMessage'.format(TELEGRAM_TOKEN) #메시지 발송 URL
    
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]

    # 마스터키 전체
    # 마스터키 ****점
    
    msg = ''
    data = ''
    txt = req["message"]["text"]
    
###############################################################################    
    if(txt.startswith('마스터키')):
        cafe_name = txt.split(" ")[1]
        cd = CAFE_LIST[cafe_name]
        if (cd > 0):
            data = master_key_info(cd)
        else:
            data = master_key_list()
        msg = []
        for d in data:
            msg.append('\n'.join(d.values()))
        msg = '\n\n'.join(msg)
###############################################################################
    elif(txt.startswith('서이룸')):
        cafe_name = txt.split(' ')
        if(len(cafe_name)>2):
            cafe_name = ' '.join(cafe_name[1:3])
        else:
            cafe_name = cafe_name[1]
        
        if(cafe_name == "전체"):
            data = seoul_escape_list()
        else:
            data = seoul_escape_info(cafe_name)
            
        msg = []
        for d in data:
            msg.append(d)
        msg = '\n\n'.join(msg)

        
###############################################################################
    elif(req["message"]["text"] == "안녕"):
        msg = "첫 만남에는 존댓말을 써야죠!" + "\n" + "바보야"
###############################################################################
    elif(req["message"]["text"] == "안녕하세요"):
        msg = "인사 잘 하신다!ㅋㅋ" + "\n" + "바보ㅋㅋㅋ"
###############################################################################
    elif(req["message"]["text"] == "환율"):
        msg = "항목 // 환율" + "\n"
        url_exc = 'https://spib.wooribank.com/pib/jcc?withyou=CMCOM0184&__ID=c012238'
        response = requests.get(url_exc).text
        soup = bs(response,'html.parser')
        
        excs = []
        li = soup.select('table tbody tr')
        for item in li:
            exc = {
                "nation" : list(item)[3].text,
                "value" : list(item)[19].text
            }
            excs.append(exc)
            
        for ls in excs:
            msg += ls["nation"] + " : " +ls["value"] + "\n"
###############################################################################
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
###############################################################################
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
###############################################################################
    elif(req["message"]["text"] == "코스피"):
        url_KOSPI = 'https://finance.naver.com/sise/sise_index.nhn?code=KOSPI'
        response = requests.get(url_KOSPI).text
        soup = bs(response,'html.parser')
        
        KOSPI = soup.select('.quotient em')[0].text
        BASETIME = soup.select('.ly_realtime span')[2].text
        
        msg = "코스피 지수 by NAVER" + " <" + BASETIME + ">" + "\n" + KOSPI
###############################################################################
    elif(req["message"]["text"] == "코스닥"):
        url_KOSDAQ = 'https://finance.naver.com/sise/sise_index.nhn?code=KOSDAQ'
        response = requests.get(url_KOSDAQ).text
        soup = bs(response,'html.parser')
        
        KOSDAQ = soup.select('.quotient em')[0].text
        BASETIME = soup.select('.ly_realtime span')[2].text
        
        msg = "코스닥 지수 by NAVER" + " <" + BASETIME + ">" + "\n" + KOSDAQ
###############################################################################
    elif(req["message"]["text"] == "코스피200"):
        url_KOSPI200 = 'https://finance.naver.com/sise/sise_index.nhn?code=KPI200'
        response = requests.get(url_KOSPI200).text
        soup = bs(response,'html.parser')

        KOSPI200 = soup.select('.subtop_sise_detail table .imp_number')[0].text
        BASETIME = soup.select('.ly_realtime span')[2].text
        
        msg = "코스피200 지수 by NAVER" + " <" + BASETIME + ">" + "\n" + KOSPI200
###############################################################################
    else:
        msg = "[등록 명령어 목록]" + "\n" + "[가능 명령어 : 환율, 네이버 웹툰, 다음 웹툰, 코스피, 코스닥, 코스피200, 마스터키, 서이룸]"

    requests.get(url,params = {"chat_id" : chat_id, "text" : msg}) # 메시지 발송시키기
    return '', 200   



"""
   # else:
   #     msg = "[등록 명령어 목록]" + "\n" + "가능 명령어 : " + "환율, 코스피, 코스닥, 네이버 웹툰, 다음 웹툰, 마스터키"

    elif(req["message"]["text"] == "내일 날씨"):
    elif(req["message"]["text"] == "미세먼지"):
    elif(req["message"]["text"] == "이름 궁합"):
    elif(req["message"]["text"] == "휘발유"):
"""
#####   
    
@app.route('/set_webhook')
def set_webhook():
    url = TELEGRAM_URL + '/bot' + TELEGRAM_TOKEN + '/setWebhook'
    
    params = {
        'url' : 'https://nwongi7-nwongi7.c9users.io/{}'.format(TELEGRAM_TOKEN)
    }
    
    response = requests.get(url, params = params).text
    return response