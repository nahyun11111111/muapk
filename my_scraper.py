import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- 1. ChromeDriver 경로 설정 ---
# 이 경로는 사용자님의 Mac에 있는 chromedriver 파일의 실제 절대 경로입니다.
# 'readlink -f chromedriver' 명령어로 확인한 경로를 사용하세요.
# 예시: '/Users/hyun/Desktop/muapk/chromedriver'
driver_path = '/Users/hyun/Desktop/muapk/chromedriver' # <--- 이 부분을 사용자님의 정확한 경로로 바꿔주세요!

# ChromeDriver 서비스 설정
service = Service(driver_path)

# Chrome WebDriver 시작
try:
    driver = webdriver.Chrome(service=service)
    print("무신사 웹사이트가 성공적으로 열렸습니다.")
    time.sleep(2) # 페이지 로딩 대기

    # --- 2. 무신사 웹사이트로 이동 ---
    driver.get('https://www.musinsa.com')
    time.sleep(3) # 페이지 로딩 대기 (충분히 기다립니다)

    # --- 3. 검색창 찾아서 검색어 입력하기 ---
    # 개발자 도구로 확인한 검색창의 CSS 선택자를 사용합니다.
    # 'input[aria-label="검색창"]'는 'aria-label' 속성값이 "검색창"인 input 태그를 찾습니다.
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="검색창"]'))
    )

    search_query = "비오는날 코디"
    search_box.send_keys(search_query) # 검색어 입력
    search_box.send_keys(Keys.RETURN) # 엔터 키를 눌러 검색 실행

    print(f"'{search_query}' 검색을 실행했습니다.")
    time.sleep(5) # 검색 결과 페이지 로딩 대기

    # --- 4. 검색 결과 페이지에서 상품 정보 추출 ---
    # HTML 소스 가져오기
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 상품 리스트 선택자 확인 (무신사 웹사이트 구조 변경 시 이 부분 수정 필요)
    # 현재는 '.search-list-box .li_box'가 상품 목록의 각 항목을 나타내는 것으로 가정합니다.
    products = soup.select('.search-list-box .li_box')

    if not products:
        print("상품을 찾을 수 없습니다. 선택자를 다시 확인해주세요.")
    else:
        for i, product in enumerate(products):
            # 상품명 추출
            product_name_element = product.select_one('.item_title a')
            product_name = product_name_element.get_text(strip=True) if product_name_element else 'N/A'

            # 가격 추출
            price_element = product.select_one('.list_price .price')
            price = price_element.get_text(strip=True) if price_element else 'N/A'

            # 이미지 URL 추출
            image_element = product.select_one('.list_img img')
            image_url = image_element['src'] if image_element and 'src' in image_element.attrs else 'N/A'

            print(f"--- 상품 {i+1} ---")
            print(f"상품명: {product_name}")
            print(f"가격: {price}")
            print(f"이미지 URL: {image_url}")
            print("-" * 20)

except Exception as e:
    # 예외 발생 시 오류 메시지 출력
    print(f"오류가 발생했습니다: {e}")

finally:
    # 드라이버 종료 (오류 발생 여부와 관계없이 항상 실행)
    if 'driver' in locals(): # driver 변수가 정의되었는지 확인
        driver.quit()
        print("브라우저가 닫혔습니다.")