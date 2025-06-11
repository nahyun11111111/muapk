from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By # 웹 요소를 찾기 위한 모듈
from selenium.webdriver.common.keys import Keys # 키보드 입력(Enter 등)을 위한 모듈
from selenium.webdriver.support.ui import WebDriverWait # 웹 요소가 나타날 때까지 기다리기 위한 모듈
from selenium.webdriver.support import expected_conditions as EC # 기다리는 조건 설정 모듈
import time
from bs4 import BeautifulSoup # HTML 파싱을 위한 BeautifulSoup 라이브러리

# 1. ChromeDriver 경로 설정
# chromedriver.exe 파일이 현재 파이썬 스크립트와 같은 폴더에 있다고 가정합니다.
# 만약 다른 폴더에 있다면, 'C:/Users/사용자이름/Downloads/chromedriver.exe'처럼 전체 경로를 입력해야 합니다.
driver_path = '/Users/hyun/Desktop/muapk/chromedriver'
service = Service(driver_path)

# 2. 크롬 브라우저 열기 (WebDriver 객체 생성)
driver = webdriver.Chrome(service=service)

try:
    # 1. 무신사 웹사이트 열기
    driver.get('https://www.musinsa.com')
    print("무신사 웹사이트가 성공적으로 열렸습니다.")
    time.sleep(2) # 페이지 로딩 대기

    # 2. 검색창 찾아서 검색어 입력하기
# CSS 선택자를 사용하여 검색창(input 태그)을 찾습니다.
# 'input[aria-label="검색창"]'는 'aria-label' 속성값이 "검색창"인 input 태그를 찾습니다.
search_box = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-label="검색창"]'))
)

search_query = "비오는날 코디"
search_box.send_keys(search_query) # 검색어 입력
search_box.send_keys(Keys.RETURN) # 엔터 키를 눌러 검색 실행

print(f"'{search_query}' 검색을 실행했습니다.")
time.sleep(5) # 검색 결과 페이지 로딩 대기

    # 3. 검색 결과 페이지의 HTML 가져오기
    # 셀레니움으로 페이지를 이동시킨 후, 그 페이지의 HTML을 BeautifulSoup으로 넘겨 파싱합니다.
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 4. 상품 정보 추출하기
    # 무신사 검색 결과 페이지에서 각 상품 아이템을 나타내는 HTML 요소를 찾습니다.
    # 이 부분은 **무신사 웹사이트의 실제 HTML 구조를 F12 개발자 도구로 확인**하고 맞춰야 합니다.
    # 아래 선택자들은 예시이며, 정확하지 않을 수 있습니다.
    
    # 상품 리스트를 포함하는 가장 큰 컨테이너를 찾습니다.
    # 예시: search-list-box 클래스를 가진 div 안에 li_box 클래스를 가진 li 태그들이 상품 하나하나를 의미한다고 가정
    product_items = soup.select('.search-list-box .li_box')

    if product_items:
        print(f"\n'{search_query}' 검색 결과 (상위 5개):")
        for i, item in enumerate(product_items[:5]): # 상위 5개만 예시로
            try:
                # 상품명 추출 (예시: item_title 클래스를 가진 a 태그 안의 텍스트)
                name_element = item.select_one('.item_title a')
                product_name = name_element.text.strip() if name_element else "이름 없음"

                # 가격 추출 (예시: price 클래스를 가진 span 태그 안의 텍스트)
                price_element = item.select_one('.price')
                product_price = price_element.text.strip() if price_element else "가격 없음"

                # 이미지 URL 추출 (lazy-loading 이미지의 경우 'data-original' 속성 확인)
                # 대부분의 쇼핑몰 이미지는 'src' 또는 'data-original' 속성에 실제 URL이 있습니다.
                image_element = item.select_one('.list_img img')
                if image_element:
                    if 'data-original' in image_element.attrs:
                        image_url = image_element['data-original']
                    elif 'src' in image_element.attrs:
                        image_url = image_element['src']
                    else:
                        image_url = "이미지 URL 없음"
                else:
                    image_url = "이미지 없음"

                print(f"상품명: {product_name}")
                print(f"가격: {product_price}")
                print(f"이미지 URL: {image_url}")
                print("-" * 30)

            except Exception as e:
                print(f"{i+1}번째 상품 처리 중 오류 발생: {e}")
                print("-" * 30)
    else:
        print("상품을 찾을 수 없습니다. 선택자를 다시 확인해주세요.")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")

finally:
    # 5. 브라우저 닫기 (오류 발생 시에도 닫히도록 finally 블록에 넣습니다)
    driver.quit()
    print("브라우저가 닫혔습니다.")