import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


driver_path = '/Users/hyun/Desktop/muapk/chromedriver' 

# ChromeDriver 서비스 설정
service = Service(driver_path)

# Chrome WebDriver 시작
try:
    driver = webdriver.Chrome(service=service)
    print("무신사 웹사이트가 성공적으로 열렸습니다.")
    time.sleep(2) # 페이지 로딩 대기

    # --- 2. 무신사 웹사이트로 이동 ---
    driver.get('https://www.musinsa.com')
    time.sleep(3) # 페이지 로딩 대기 (

    # --- 3. 검색창 찾아서 검색어 입력하기 ---
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="검색창"]'))
    )

    search_query = "비오는날 코디" # 원하는 검색어로 변경 가능합니다.
    search_box.send_keys(search_query) # 검색어 입력
    search_box.send_keys(Keys.RETURN) # 엔터 키를 눌러 검색 실행

    print(f"'{search_query}' 검색을 실행했습니다.")
    time.sleep(5) # 검색 결과 페이지 로딩 대기

    # --- 4. '스냅/코디' 탭 클릭하기 ---
    try:
        # 'data-mds' 속성과 텍스트 내용으로 '스냅/코디' 탭 버튼을 찾습니다.
        snap_coordi_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-mds='TabTextItem' and text()='스냅/코디']"))
        )
        snap_coordi_tab.click()
        print("'스냅/코디' 탭을 클릭했습니다.")
        time.sleep(5) # 스냅/코디 결과 로딩 대기

    except Exception as e:
        print(f"'스냅/코디' 탭을 클릭하는 중 오류 발생 또는 탭을 찾을 수 없습니다: {e}")
        # 탭을 찾지 못해도 스크립트가 멈추지 않도록 예외 처리

    # --- 5. 스냅/코디 결과 페이지에서 정보 추출 ---
    # HTML 소스 가져오기 (탭 클릭 후 새로 로딩된 페이지 소스)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 스냅/코디 리스트 선택자를 찾은 클래스 이름으로 변경합니다.
    # .gIhsno 클래스를 가진 div 태그를 찾습니다.
    snap_items = soup.select('div.gIhsno') 
    if not snap_items:
        print("스냅/코디 아이템을 찾을 수 없습니다. 스냅/코디 페이지의 선택자를 다시 확인해주세요.")
    else:
        print("\n--- 스냅/코디 검색 결과 ---")
        for i, item in enumerate(snap_items):
            # 이미지 URL 추출
            image_element = item.select_one('img') # 각 스냅 아이템 내의 img 태그
            image_url = image_element['src'] if image_element and 'src' in image_element.attrs else 'N/A'

            # 스냅/코디 상세 페이지 링크 추출
            # a 태그의 href 속성에서 링크를 가져옵니다.
            link_element = item.select_one('a.gtm-click-content') # 해당 링크를 감싸는 a 태그
            full_link = link_element['href'] if link_element and 'href' in link_element.attrs else 'N/A'

            # (참고) 제목은 스냅/코디 목록 페이지에서 직접 추출하기 어렵습니다.
            # 상세 페이지로 이동해야 얻을 수 있는 경우가 많습니다.
            # 현재는 이미지 URL과 링크만 출력합니다.

            print(f"--- 스냅/코디 {i+1} ---")
            print(f"이미지 URL: {image_url}")
            print(f"링크: {full_link}")
            print("-" * 20)

except Exception as e:
    # 예외 발생 시 오류 메시지 출력
    print(f"스크립트 실행 중 오류가 발생했습니다: {e}")

finally:
    # 드라이버 종료 (오류 발생 여부와 관계없이 항상 실행)
    if 'driver' in locals(): 
        driver.quit()
        print("브라우저가 닫혔습니다.")