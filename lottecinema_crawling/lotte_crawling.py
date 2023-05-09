# 웹 브라우저와 연동을 위해
from selenium import webdriver
# Chrome 객체의 인자로 넣기 위해
from selenium.webdriver.chrome.service import Service
# 사용 중인 Chrome version과의 싱크를 맞추기 위해
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from datetime import date
import requests
import time

def getCinemaId():
    cinemaID_dict = {}

    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get("https://www.lottecinema.co.kr/NLCHS/Ticketing/Schedule")
        driver.implicitly_wait(10)
        
        cinemaID = []
        for i in range(1, 25): # (1~24) 서울 영화관 고유 아이디 추출
            element = driver.find_element(By.XPATH, '//*[@id="nav"]/ul/li[3]/div/ul/li[2]/div/ul/li[{}]/a'.format(i))
            
            href = element.get_attribute("href")  # href 속성 값을 가져옵니다.
            cinemaID.append(href[-4:])  # href 값을 출력합니다.
            
        cinemaID_dict["서울"] = cinemaID
        
        cinemaID = []
        for i in range(1, 48): # (1~48) 경기/인천 영화관 고유 아이디 추출
            element = driver.find_element(By.XPATH, '//*[@id="nav"]/ul/li[3]/div/ul/li[3]/div/ul/li[{}]/a'.format(i))
            
            href = element.get_attribute("href")
            cinemaID.append(href[-4:])
            
            cinemaID_dict["경기/인천"] = cinemaID

    return cinemaID_dict

def findDistrictByCinemaID(cinemaID_dict):

    district_dict = {}
    citys = {"서울" : "1", "경기/인천" : "2"}
    for city in cinemaID_dict:
        
        cinemaID_list = cinemaID_dict[city]
        for cinema_id in cinemaID_list: # ['1013', '9094', '9010', '1004', ...
            webdriver_options = webdriver.ChromeOptions()
            webdriver_options.add_argument('headless') # 화면 안보이기
            url = f'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode={citys[city]}&cinemaID={cinema_id}'
    
            with webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = webdriver_options) as driver:
                driver.get(url)
                driver.implicitly_wait(10)
                
                try:
                    driver.find_element(By.CSS_SELECTOR, '#layerGetPopup > div.layer_header > button').click()
                except:
                    try:
                        driver.find_element(By.CSS_SELECTOR, '#layerPopupMulti > li > div.layer_footer.ty2 > ul > li > button').click()
                    except:
                        pass                    
                
                district = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div[2]/dl[1]/dd[3]').text.split()[1]
                theater_name = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div[1]/h3').text 
                
                print(theater_name, district)
                district_dict[theater_name] = district
                
    return district_dict

# findDistrictByCinemaID()의 결과
district_dict = {'가산디지털': '금천구', '가양': '강서구', '강동': '강동구', '건대입구': '광진구', '김포공항': '강서구', '노원': '노원구', '도곡': '강남구', '독산': '금천구', '브로드웨이(신사)': '강남구', '서울대입구': '관악구', '수락산': '노원구', '수유': '강북구', '신대방(구로디지털역)': '동작구', '신도림': '구로구', '신림': '관악구', '에비뉴엘(명동)': '중구', '영등포': '영등포구', '용산': '용산구', '월드타워': '송파구', '은평(롯데몰)': '은평구', '중랑': '중랑구', '청량리': '동대문구', '합정': '마포구', '홍대입구': '마포구', '광교아울렛': '수원시', '광명(광명사거리)': '광명시', '광명아울렛': '광명시', '광주터미널': '광주시', '구리아울렛': '구리시', '동탄': '화성시', '라페스타': '고양시', '마석': '남양주시', '별내': '남양주시', '병점': '화성시', '부천(신중동역)': '부천시', '부천역': '부천시', '부평': '부평구', '부평갈산': '부평구', '부평역사': '부평구', '북수원(천천동)': '수원시', '산본피트인': '군포시', '서수원': '수원시', '성남중앙(신흥역)': '성남시', '센트럴락': '안산시', '송탄': '평택시', '수원(수원역)': '수원시', '수지': '용인시', '시화(정왕역)': '시흥시', '시흥장현': '시흥시', '안산': '안산시', '안산고잔': '안산시', '안성': '안성시', '안양(안양역)': '안양시', '안양일번가': '안양시', '영종하늘도시': '중구', '오산(원동)': '오산시', '용인기흥': '용인시', '용인역북': '용인시', '위례': '성남시', '의정부민락': '의정부시', '인덕원': '안양시', '인천아시아드': '서구', '인천터미널': '미추홀구', '주엽': '고양시', '진접': '남양주시', '파주운정': '파주시', '판교(창조경제밸리)': '성남시', '평촌(범계역)': '안양시', '평택비전(뉴코아)': '평택시', '하남미사': '하남시', '향남': '화성시'}

def getMovieInfo():
    today = date.today()
    today_date = today.strftime("%Y-%m-%d")

    url = "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx"
    citys = {"서울" : "0001", "경기/인천" : "0002"}
    cinemaID_dict = getCinemaId()
    all_movie = []

    for city in citys:
        cinemaID_list = cinemaID_dict[city] # ['1013', '9094', '9010', '1004', ...
        city_id = citys[city] # 0001
        for cinema_id in cinemaID_list:
            time.sleep(1) # 요청 전에 딜레이를 줌
            dic = {"MethodName":"GetPlaySequence",
            "channelType":"HO",
            "osType":"",
            "osVersion":"",
            "playDate":today_date,
            "cinemaID":"1|{}|{}".format(city_id, cinema_id),
            "representationMovieCode":""
            }
            parameters = {"paramList": str(dic)}    
            response = requests.post(url, data = parameters).json()
            movies_response = response['PlaySeqs']['Items']

            for move_res in movies_response:
                move_data = {"theater_type":"LOTTE CINEMA", "theater_name":move_res['CinemaNameKR'], "location":city, "district":district_dict[move_res['CinemaNameKR']], "movie_title":move_res['MovieNameKR'], "start_time":move_res['StartTime']}
                all_movie.append(move_data)

    return all_movie

if __name__ == '__main__':
    getMovieInfo()
