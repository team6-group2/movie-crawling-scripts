from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time


def crawling_title_starttime(areacode, theaterCode, theaterName, table, driver):
    if areacode=="01":
        location="서울"
    elif areacode=="02":
        location="경기도"
    elif areacode=="202":
        location="인천"

    try:
        driver.get(f"http://www.cgv.co.kr/theaters/?areacode={areacode}&theaterCode={theaterCode}&date=20230502")
        driver.implicitly_wait(10)
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
                    table=pd.concat([table, pd.DataFrame([["CGV", theaterName, location, movie_title, start_time]], columns=["theater_type", "theater_name", "location", "movie_title", "start_time"])],ignore_index=True)
                    # print(start_time)
        return table
    except Exception as error:
        # print(error)
        return table


def crawling_location_theatername():
    soup=BeautifulSoup(requests.get("http://www.cgv.co.kr/theaters/").text, "html.parser")
    script=soup.find("div", id="contents").script.string
    expression = r'"RegionCode":\s*"([^"]*)"\s*,\s*"TheaterCode":\s*"([^"]*)"\s*,\s*"TheaterName":\s*"([^"]*)'
    matches = re.findall(expression, script, re.DOTALL)
    movie_table = pd.DataFrame(columns=["theater_type", "theater_name", "location", "movie_title", "start_time"])
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for match in matches:
        if match[0] in ["01", "02", "202"]:
            movie_table=crawling_title_starttime(match[0], match[1], match[2], movie_table, driver)
            time.sleep(0.5)
        else:
            break
    driver.quit()

    print(movie_table)


if __name__=="__main__":
    crawling_location_theatername()
    