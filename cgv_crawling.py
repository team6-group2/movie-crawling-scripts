from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time
from datetime import date

def crawling_title_starttime(areacode, theaterCode, theaterName, today, json, driver):
    if areacode=="01":
        city="서울"
    elif areacode=="02":
        city="경기"
    elif areacode=="202":
        city="인천"


    try:
        driver.get(f"http://www.cgv.co.kr/theaters/?areacode={areacode}&theaterCode={theaterCode}&date={today}")
        driver.implicitly_wait(10)
        district=driver.find_element(By.XPATH, "//*[@id='contents']/div[2]/div[1]/div/div[2]/div[1]/strong").text
        if areacode=="02":
            district=re.search(r"\b\w+시\b", district).group()
        else:
            district=re.search(r"\b\w+구\b", district).group()
        #print(district)
        iframe=driver.find_element(By.XPATH, "//iframe[@id='ifrm_movie_time_table']")
        driver.switch_to.frame(iframe)
        iframe_page_source=BeautifulSoup(driver.page_source, "html.parser")
        movies_data=iframe_page_source.select("body > div > div.sect-showtimes > ul > li")
        for movie_data in movies_data:
            movie_title=movie_data.div.find("div", "info-movie").a.text.strip()
            # print(movie_title)
            halls=movie_data.div.find_all("div", "type-hall")
            for hall in halls:
                time_table=hall.select("div.info-timetable > ul > li")
                # print(time_table)
                for t in time_table:
                    start_time=t.em.text
                    if not start_time:
                        start_time=t.a.em.text
                    json["CGV"].append({"theater_type": "CGV", "theater_name": theaterName, "city": city, "district":district, "movie_title": movie_title, "start_time": start_time })
                    # print(start_time)
        return json
    except Exception as error:
        # print(error)
        return json


def crawling_city_theatername():
    soup=BeautifulSoup(requests.get("http://www.cgv.co.kr/theaters/").text, "html.parser")
    script=soup.find("div", id="contents").script.string
    expression = r'"RegionCode":\s*"([^"]*)"\s*,\s*"TheaterCode":\s*"([^"]*)"\s*,\s*"TheaterName":\s*"([^"]*)'
    matches = re.findall(expression, script, re.DOTALL)
    movie_json = {"CGV":[]}
    today=date.today().strftime("%Y%m%d")
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for match in matches:
        if match[0] in ["01", "02", "202"]:
            movie_json=crawling_title_starttime(match[0], match[1], match[2], today, movie_json, driver)
            time.sleep(0.5)
        else:
            break
    driver.quit()

    print(movie_json)
    return movie_json


if __name__=="__main__":
    crawling_city_theatername()
    
