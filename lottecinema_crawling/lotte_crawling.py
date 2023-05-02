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
                # 상영 시작 시간과 종료 시간을 시간 형식으로 변환
                start_hour, start_minute = map(int, move_res['StartTime'].split(':'))
                end_hour, end_minute = map(int, move_res['EndTime'].split(':'))
                # 러닝타임 계산
                running_time = (end_hour - start_hour) * 60 + (end_minute - start_minute)
                
                move_data = {"theater_type":"롯데시네마", "theater_name":move_res['CinemaNameKR'], "location":city, "movie_title":move_res['MovieNameKR'], "start_time":move_res['StartTime'], "running_time":running_time}

                all_movie.append(move_data)

    return all_movie

if __name__ == '__main__':
    getMovieInfo()