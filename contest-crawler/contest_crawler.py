from selenium import webdriver  # Selenium을 사용해 브라우저를 열기 위해
from selenium.webdriver.common.by import By  # HTML 요소 탐색을 위해
from selenium.webdriver.support.ui import WebDriverWait  # 브라우저 응답을 기다리기 위해
from selenium.webdriver.support import (
    expected_conditions as EC,
)  # HTML 요소 상태 체크를 위해
from datetime import datetime, timedelta  # 날짜 및 시간 계산을 위해
import time  # 대기 시간 설정을 위해
import re  # 정규 표현식을 사용하기 위해
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import contest_db

def dev_crawling(driver):
    wait = WebDriverWait(driver, 10)
    all_data = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "Item_item__HzT1B")))

    data_list1 = []
    # 날짜 형식 YYYY.MM.DD를 찾는 정규 표현식 패턴
    date_pattern = r"\d{4}\.\d{2}\.\d{2}"
    time.sleep(3)

    for item in all_data:
        href = item.find_element(By.TAG_NAME, "a").get_attribute("href")
        name = item.find_element(By.CLASS_NAME, "Item_item__content__title__94_8Q").text
        opener = item.find_element(By.CLASS_NAME, "Item_host__3dy8_").text
        date = item.find_element(By.CLASS_NAME, "Item_date__date__CoMqV").text
        img = item.find_element(By.TAG_NAME, "img").get_attribute("src")

        dates = re.findall(date_pattern, date)
        ex_start = datetime.strptime(dates[0], "%Y.%m.%d").date() if dates else None
        ex_end = (
            datetime.strptime(dates[1], "%Y.%m.%d").date() if len(dates) > 1 else None
        )

        activity_data = {
            "ex_name": name,
            "ex_link": href,
            "ex_host": opener,
            "ex_image": img,
            "ex_start": ex_start,
            "ex_end": ex_end,
            "ex_flag": 1,
        }
        data_list1.append(activity_data)
    # print(data_list1)
    return data_list1


def link_crawling(driver):
    wait = WebDriverWait(driver, 30)
    data_list2 = []
    index = 0

    while True:
        try:
            # 모든 항목을 다시 불러오기
            all_items = wait.until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, ".activity-list-card-item-wrapper")
                )
            )

            # 만약 인덱스가 목록을 초과하면 종료
            if index >= len(all_items):
                break

            item = all_items[index]
            try:
                # 각 항목의 링크 클릭
                link_element = item.find_element(By.CSS_SELECTOR, "a.image-link")
                driver.execute_script("arguments[0].click();", link_element)
                time.sleep(5)

                # 데이터 추출
                name = driver.find_element(By.TAG_NAME, "h1").text
                opener = driver.find_element(By.CLASS_NAME, "organization-name").text

                # 날짜 형식 패턴 (예: YYYY.MM.DD)
                date_pattern = r"\d{4}\.\d{2}\.\d{2}"

                # 모든 <span> 요소 가져오기
                spans = driver.find_elements(By.TAG_NAME, "span")
                # print(name, opener)
                # 날짜 초기화
                start_date = None
                end_date = None

                # 각 <span> 요소의 텍스트 확인
                for span in spans:
                    text = span.text
                    # 정규 표현식을 사용하여 날짜 형식과 일치하는지 확인
                    if re.match(date_pattern, text):
                        if not start_date:
                            start_date = datetime.strptime(
                                text, "%Y.%m.%d"
                            ).date()  # 첫 번째로 찾은 날짜는 시작일로 설정
                        elif not end_date:
                            end_date = datetime.strptime(
                                text, "%Y.%m.%d"
                            ).date()  # 두 번째로 찾은 날짜는 종료일로 설정
                            break  # 종료일을 찾으면 반복 중단
                
                try:
                    # 이미지 URL 가져오기 (src가 실제 URL로 설정될 때까지 대기)
                    img_element = driver.find_element(By.CLASS_NAME, "card-image")
                    WebDriverWait(driver, 15).until(
                        lambda driver: img_element.get_attribute("src").startswith("http")
                    )
                    # 이미지 URL을 가져옴
                    img = img_element.get_attribute("src")

                except Exception:
                    img = None
                    
                # 현재 페이지의 URL을 저장
                current_url = driver.current_url
                # print(img, current_url)
                # 수집한 데이터를 딕셔너리에 저장
                activity_data = {
                    "ex_name": name,
                    "ex_link": current_url,
                    "ex_host": opener,
                    "ex_image": img,
                    "ex_start": start_date,
                    "ex_end": end_date,
                    "ex_flag": 2,
                }
                data_list2.append(activity_data)
                # print(activity_data)
                # 데이터를 수집한 후 이전 페이지로 돌아감
                driver.back()
                time.sleep(3)  # 페이지 로드 대기

                # 다음 항목으로 이동하기 위해 인덱스 증가
                index += 1

            except Exception as e:
                print(f"데이터 수집 중 오류 발생: {e}")
                driver.back()  # 오류 발생 시 이전 페이지로 돌아가기
                time.sleep(3)
                # 인덱스를 증가시켜 다음 항목으로 이동
                index += 1

        except Exception as e:
            print(f"목록을 다시 로드하는 중 오류 발생: {e}")
            time.sleep(3)

    # 수집한 모든 데이터 출력
    # print(data_list2)
    return data_list2


def main():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    crawling_data = []

    try:
        print("Starting dev-event crawling...")
        driver.get("https://dev-event.vercel.app/events")
        crawling_data.extend(dev_crawling(driver))
        print(f"Finished dev-event crawling. (Collected {len(crawling_data)} items)")

        print("Starting linkareer crawling...")
        driver.get(
            "https://linkareer.com/list/contest?filterBy_categoryIDs=35&filterType=CATEGORY&orderBy_direction=DESC&orderBy_field=CREATED_AT&page=1"
        )
        crawling_data.extend(link_crawling(driver))
        print(crawling_data)
        
        if crawling_data:
            contest_db.save_to_db(crawling_data)
            print("Saved to contest_info.db.")
        else:
            print("No data was crawled.")
            
    finally:
        driver.quit()
        print("Driver quit. Process finished.")


if __name__ == "__main__":
    main()