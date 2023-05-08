import pandas as pd
import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service #
from webdriver_manager.chrome import ChromeDriverManager # 
from selenium.webdriver.common.by import By
import json



def theater_crawl(result, theater_name, theater_name_url):
    '''영화관 지점별 크롤링'''
    
    webdriver_options = webdriver.ChromeOptions()
    webdriver_options.add_argument('headless') # 화면 안보이기
    # driver_detail = webdriver.Chrome(service=Service(ChromeDriverManager().install())) # 
    driver_detail = webdriver.Chrome(ChromeDriverManager().install(), options=webdriver_options )
    driver_detail.get(theater_name_url)
    driver_detail.implicitly_wait(2)

    # 시, 구 가져오기 
    address = driver_detail.find_element(By.CSS_SELECTOR, '#tab01 > ul:nth-child(9) > li').text
    driver_detail.implicitly_wait(2)
    district = address.strip().split(' ')[3]

    # 상영시간표 누르기
    driver_detail.find_element(By.CSS_SELECTOR, '#contents > div.inner-wrap.pt40 > div.tab-list.fixed.mb40.tab-layer > ul > li:nth-child(2) > a').click()
    driver_detail.implicitly_wait(2)

    # 12시에 들어갔을 때 아직 날짜가 안바뀐 것을 볼 수 있음 -> 다음 날로 눌러주기
    driver_detail.find_element(By.CSS_SELECTOR, '#tab02 > div.time-schedule.mb30 > div > div.date-list > div.date-area > div > button:nth-child(3)').click()
    driver_detail.implicitly_wait(3)

    

    # 영화 제목별 ex) 슈퍼마리오
    movie_elements = driver_detail.find_elements(By.CSS_SELECTOR, '#tab02 > div.reserve.theater-list-box > div.theater-list')
    for movie_element in movie_elements:
        movie_title = movie_element.find_element(By.CSS_SELECTOR, 'div.theater-tit > p:nth-child(2) > a').text
        start_time_elements = movie_element.find_elements(By.CSS_SELECTOR, 'p.time')

        for start_time_element in start_time_elements:
            # 상영 시각
            start_time = start_time_element.text
            result.append(['MEGABOX']+ [theater_name]+ ['']+ [movie_title] + [start_time] + [district])
            print(['MEGABOX']+ [theater_name]+ ['']+ [movie_title] + [start_time] + [district])
    
    driver_detail.quit()

    return result
    


def city_crawl(driver, location_element):
    '''지역별 크롤링'''
    result = []
    location_element.click()
    theater_name_elements = driver.find_elements(By.CSS_SELECTOR, 'div.theater-place > ul > li.on > div > ul > li > a')


    for theater_name_element in theater_name_elements:
        # 테스트
        
        theater_name_url = theater_name_element.get_attribute('href')
        theater_name = theater_name_element.text
        
        
        # 지점별 상영시간 크롤링 
        result = theater_crawl(result, theater_name, theater_name_url)
        print(f'{theater_name} 완료')
    
    print(result)
    movie_tbl = pd.DataFrame(result,  columns=('theater_type',  'theater_name', 'city', 'movie_title', 'start_time', 'district'))
    return movie_tbl
        
def megabox_crawl():
    print('>>> 크롤링 시작')
    main_url = 'https://www.megabox.co.kr/theater/list'
    webdriver_options = webdriver.ChromeOptions()
    webdriver_options.add_argument('headless') # 화면 안보이기

    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options) # 
    driver.get(main_url)

    # 서울, 경기, 인천
    location_elements = driver.find_elements(By.CSS_SELECTOR, 'li > button.sel-city')
    # movie_total = pd.DataFrame(columns=('theater_type'  'theater_name' 'location' 'movie_title' 'start_time' 'run_time'))
    # 앞 3개만 크롤링 (서울, 경기, 인천) / 0, 1, 2
    city = {0:'서울', 1:'경기', 2:'인천'}
    for i in range(3):
        # # 테스트 
        # if i ==1 :
        #     break

        print(f'>>> {city[i]} 시작')
        movie_tbl = city_crawl(driver, location_elements[i])
        movie_tbl['city'] = city[i]
        print(f'>>> {city[i]} 완료')
    
        try:
            movie_total = pd.concat([movie_total, movie_tbl])
        except:
            movie_total = movie_tbl

    
    movie_total.to_csv(f'메가박스 상영시간_{datetime.datetime.now()}.csv', encoding='utf-8', index = False )
    movie_total.to_json('메가박스 상영시간.json', orient='records', force_ascii=False)
    
    print('저장완료')
    driver.quit()


if __name__ == '__main__':
    megabox_crawl()
    