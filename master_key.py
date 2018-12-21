from bs4 import BeautifulSoup as bs
import requests

def master_key_info(cd):
    url = "http://www.master-key.co.kr/booking/booking_list_new"
    params = {
        "date" : "2018-12-22",
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
    
#####
def master_key_list():
    url = 'http://www.master-key.co.kr/home/office'
    
    response = requests.get(url).text
    soup = bs(response, 'html.parser')
    lis = soup.select('.escape_list .escape_view')
    
    cafe_list = []
    url_base = 'https://www.master-key.co.kr'
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
            'link' : link
        }
        
        cafe_list.append(cafe)
    return(cafe_list)

# 사용자로부터 '마스터키 ****점' 이라는 메시지를 받으면
# 해당 지점에 대한 오늘의 정보를 요청하고(크롤링), 
# 메시지(예약정보)를 보내준다.
print(master_key_info(2))    

#for cafe in master_key_list():
#   print(cafe['title'], ":", cafe['link'].split("=")[1])