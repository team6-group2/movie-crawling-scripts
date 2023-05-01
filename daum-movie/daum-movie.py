import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = 'https://movie.daum.net/premovie/theater'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/96.0.4664.45 Safari/537.36'
}

options = webdriver.ChromeOptions()
options.add_argument("headless")

driver = webdriver.Chrome('./chromedriver/chromedriver_mac_arm64/chromedriver', options=options)
driver.get(url)
time.sleep(2)

# WebDriverWait 객체 생성
wait = WebDriverWait(driver, 10)
movie_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ol.list_movieranking.aniposter_movie')))
movies = movie_element.find_elements(By.TAG_NAME, 'li')

links = []
# 현재 상영작 링크 가져오기
for movie in movies:
    links.append(movie.find_element(By.TAG_NAME, 'a').get_attribute('href'))

movie_data = []
for link in links:
    driver.get(link)
    time.sleep(2)

    data = {'제목': driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div/div[1]/div[2]/div[1]/h3/span[1]')[0].text}

    # 감독 및 배우 가져오기
    crew_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.list_crewall')))
    crews = crew_element.find_elements(By.TAG_NAME, 'li')

    director = []
    actor = []
    for crew in crews:
        name = crew.find_element(By.CSS_SELECTOR, 'a.link_tit').text

        if crew.find_element(By.CSS_SELECTOR, 'span.txt_info').text == '감독':
            director.append(name)
        else:
            actor.append(name)

    data['감독'] = director
    data['배우'] = actor

    # 영화 상세 정보 가져오기
    dt_elements = driver.find_elements(By.CSS_SELECTOR, 'dt')
    dd_elements = driver.find_elements(By.CSS_SELECTOR, 'dd')

    items = list(zip(dt_elements, dd_elements))

    # 딕셔너리 생성하여 값 추가하기
    for item in items:
        key = item[0].text
        value = item[1].text

        if key == '장르':
            data[key] = value.split('/')
        elif key == '국가':
            data[key] = value.split(', ')
        elif key == '러닝타임':
            data[key] = int(value[:-1])
        elif key in ['개봉', '등급']:
            data[key] = value

    print(data)
    movie_data.append(data)

# webdriver 종료
driver.quit()
