from flask import Flask, render_template, request, jsonify 
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests
import random

app = Flask(__name__)

# --- 1. ChromeDriver
driver_path = '/Users/hyun/Desktop/muapk/chromedriver' 

# --- 2. OpenWeatherMap API 설정 ---
OPENWEATHER_API_KEY = "6155529344f541a727b2742c6307ebd1"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# --- 2.1. 기온별 코디 키워드 정의 ---
TEMPERATURE_KEYWORDS = [
    {"min_temp": 27, "keyword": "한여름 코디", "outfit_desc": "민소매, 반팔, 반바지, 린넨 옷"}, # 27°C 이상
    {"min_temp": 23, "keyword": "여름 코디", "outfit_desc": "반팔, 얇은 셔츠, 반바지, 얇은 면바지"},  # 23°C ~ 26.99°C
    {"min_temp": 17, "keyword": "간절기 코디", "outfit_desc": "얇은 가디건, 얇은 니트, 맨투맨, 긴팔티, 면바지"}, # 17°C ~ 22.99°C
    {"min_temp": 9, "keyword": "쌀쌀한날 코디", "outfit_desc": "자켓, 트렌치코트, 니트, 가디건, 청바지"}, # 9°C ~ 16.99°C
    {"min_temp": 5, "keyword": "초겨울 코디", "outfit_desc": "두꺼운 코트, 경량 패딩, 히트텍, 기모바지"}, # 5°C ~ 8.99°C
    {"min_temp": -100, "keyword": "한겨울 코디", "outfit_desc": "롱패딩, 아주 두꺼운 코트, 목도리, 장갑, 내복"}, # 4°C 이하
]

# --- 3. 도시별 위도/경도 매핑 ---
CITY_COORDS = {
    "서울": {"lat": 37.5665, "lon": 126.9780},
    "부산": {"lat": 35.1796, "lon": 129.0756},
    "제주": {"lat": 33.4890, "lon": 126.4983},
    "대전": {"lat": 36.3504, "lon": 127.3845},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "울산": {"lat": 35.5384, "lon": 129.3114},
    "인천": {"lat": 37.4563, "lon": 126.7052},
    "여수": {"lat": 34.7600, "lon": 127.6622},
    "강릉": {"lat": 37.7519, "lon": 128.8748},
    "청주": {"lat": 36.6433, "lon": 127.4897},
    "천안": {"lat": 36.8140, "lon": 127.1143},
    "전주": {"lat": 35.8214, "lon": 127.1088},
    "포항": {"lat": 36.0315, "lon": 129.3512},
    "창원": {"lat": 35.2285, "lon": 128.6818},
    "수원": {"lat": 37.2635, "lon": 127.0286},
    "춘천": {"lat": 37.8814, "lon": 127.7292},
    "원주": {"lat": 37.3422, "lon": 127.9257},
    "안동": {"lat": 36.5739, "lon": 128.7291},
    "구미": {"lat": 36.1154, "lon": 128.3475},
    "군산": {"lat": 35.9734, "lon": 126.7093},
    "목포": {"lat": 34.7938, "lon": 126.3917},
    "순천": {"lat": 34.9482, "lon": 127.5342},
    "경주": {"lat": 35.8563, "lon": 129.2238},
}

# --- 기온에 따라 적절한 코디 키워드를 반환하는 함수 ---
def get_weather_keyword_from_temp(temperature):
    for temp_range in TEMPERATURE_KEYWORDS:
        if temperature >= temp_range["min_temp"]:
            return temp_range["keyword"], temp_range["outfit_desc"]
    return "알 수 없는 날씨 코디", "확인 필요"

# --- 날씨 정보를 가져와 단일 코디 키워드를 결정하는 함수 ---
def get_weather_info_and_keywords(city):
    coords = CITY_COORDS.get(city)

    params = {
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "kr"
    }

    if coords:
        params["lat"] = coords["lat"]
        params["lon"] = coords["lon"]
        print(f"[날씨 API] '{city}'에 대한 위도/경도 정보 사용: {coords['lat']}, {coords['lon']}")
    else:
        params["q"] = city
        print(f"[날씨 API] '{city}'에 대한 위도/경도 정보가 없어 도시명으로 검색을 시도합니다.")

    try:
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()

        temperature = weather_data["main"]["temp"]
        weather_description = weather_data["weather"][0]["description"]

        print(f"[날씨 API] {city} 날씨: {temperature}°C, {weather_description}")

        temp_keyword, outfit_desc = get_weather_keyword_from_temp(temperature)

        search_keyword_combined = temp_keyword 

        return {
            "search_keyword": search_keyword_combined,
            "temperature": temperature,
            "weather_description": weather_description,
            "outfit_desc": outfit_desc
        }

    except requests.exceptions.Timeout:
        print("[날씨 API] 날씨 정보를 가져오는 데 시간이 초과되었습니다.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[날씨 API] 날씨 정보를 가져오는 중 네트워크 또는 API 오류 발생: {e}")
        return None
    except KeyError:
        print(f"[날씨 API] 날씨 데이터 파싱 중 오류 발생. 응답 형식이 예상과 다릅니다. (API 키 오류 또는 도시명 오류 가능성)")
        print(f"수신된 날씨 데이터 (디버깅): {weather_data if 'weather_data' in locals() else '데이터 없음'}")
        return None
    except Exception as e:
        print(f"[날씨 API] 예상치 못한 오류 발생: {e}")
        return None

# --- 무신사 코디 스크래핑 핵심 함수 정의 ---
def scrape_musinsa_coordi(search_query, num_results=10):
    service = Service(driver_path)
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--headless') 

    driver = None
    results = []

    try:
        driver = webdriver.Chrome(service=service, options=options)
        print(f"[스크래퍼] 무신사 웹사이트를 엽니다.")

     
        driver.get('https://www.musinsa.com/main/musinsa/recommend?skip_bf=Y&gf=A')
        print(f"[스크래퍼] 무신사 추천 페이지로 이동했습니다. (팝업 스킵 시도)")
        time.sleep(7)

        initial_search_trigger_button = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-button-id="search_window"]'))
        )

        initial_search_trigger_button.click()
        print("[스크래퍼] 초기 검색창 버튼을 클릭했습니다 (검색 모달 활성화 시도).")
        time.sleep(4)

        # 2. 모달 내부에 나타난 실제 검색 입력 필드 찾기
        modal_search_box = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.search-home-search-bar-keyword'))
        )
        print("[스크래퍼] 모달 내부의 실제 검색창을 찾았습니다.")

        modal_search_box.clear()
        modal_search_box.send_keys(search_query)
        print(f"[스크래퍼] 검색어 '{search_query}'를 모달 내부 검색창에 입력했습니다.")

        # 3. 모달 내부에 있는 검색 버튼 클릭
        try:
            search_button = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-button-id="search_button"]'))
            )
            search_button.click()
            print("[스크래퍼] 모달 내부 검색 버튼을 클릭했습니다.")
        except Exception as e:
            print(f"[스크래퍼] 모달 내부 검색 버튼을 찾거나 클릭하는 중 오류 발생: {e}")
            print("[스크래퍼] 엔터 키를 눌러 검색을 시도합니다.")
            modal_search_box.send_keys(Keys.RETURN)

        print(f"[스크래퍼] 검색을 실행했습니다.")


        WebDriverWait(driver, 40).until(EC.url_contains('/search/goods'))
        print("[스크래퍼] 검색 결과 페이지로 성공적으로 이동했습니다.")
        time.sleep(7)

        # '스냅/코디' 탭 클릭
        try:
            snap_coordi_tab = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-button-name="스냅/코디"]'))
            )
            snap_coordi_tab.click()
            print("[스크래퍼] '스냅/코디' 탭을 클릭했습니다.")
            time.sleep(7)

        except Exception as e:
            print(f"[스크래퍼] '스냅/코디' 탭을 찾거나 클릭하는 중 오류 발생: {e}")
            print("[스크래퍼] '스냅/코디' 탭 클릭 없이 현재 페이지에서 코디 아이템을 찾습니다.")


        # HTML 소스 가져오기 및 BeautifulSoup 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 스냅/코디 아이템 선택
        snap_items = soup.select('div.sc-d36st-1.gIhsno, .style-list-item, li.style-list-item')

        if not snap_items:
            print("[스크래퍼] 스냅/코디 아이템을 찾을 수 없습니다.")
        else:
            print(f"[스크래퍼] 총 {len(snap_items)}개의 스냅/코디 아이템을 찾았습니다.")
            # 요청된 개수만큼 처리 
            if num_results == 1:
                items_to_process = [random.choice(snap_items)] if snap_items else []
            else:
                items_to_process = snap_items[:num_results]


            for i, item in enumerate(items_to_process):
                image_element = item.select_one('img')
                image_url = image_element['src'] if image_element and 'src' in image_element.attrs else \
                            (image_element['data-src'] if image_element and 'data-src' in image_element.attrs else 'N/A')

                link_element = item.select_one('a.gtm-click-content, a.style-list-item__link')
                full_link = link_element['href'] if link_element and 'href' in link_element.attrs and not link_element['href'].startswith('javascript') else 'N/A'

                if full_link == 'N/A' and link_element and 'onclick' in link_element.attrs:
                    onclick_attr = link_element['onclick']
                    match = re.search(r"goView\('(\d+)'\)", onclick_attr)
                    if match:
                        item_id = match.group(1)
                        full_link = f"https://www.musinsa.com/app/styles/detail/{item_id}"

                # URL 정규화
                if image_url != 'N/A':
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/images/'):
                        image_url = 'https://image.musinsa.com' + image_url
                    elif not re.match(r'https?://', image_url) and not image_url.startswith('data:image'):
                        image_url = 'https://www.musinsa.com' + image_url

                if full_link != 'N/A' and not re.match(r'https?://', full_link) and not full_link.startswith('javascript'):
                    full_link = 'https://www.musinsa.com' + full_link

                results.append({'image_url': image_url, 'link': full_link})

    except Exception as e:
        print(f"[스크래퍼] 스크래핑 중 전반적인 오류가 발생했습니다: {type(e).__name__}: {e}")
        return None

    finally:
        if driver:
            driver.quit()
            print("[스크래퍼] 브라우저가 닫혔습니다.")
        return results

# --- 무작위 코디 추천을 위한 스크래핑 함수 ---
def scrape_random_coordi_item():
    service = Service(driver_path)
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--headless') # Flask 앱은 백그라운드에서 실행되므로 headless 모드 사용

    driver = None
    random_coordi = None

    try:
        driver = webdriver.Chrome(service=service, options=options)
        print(f"[스크래퍼] 무신사 코디 페이지를 엽니다.")

        driver.get('https://www.musinsa.com/app/styles/lists')
        print(f"[스크래퍼] 무신사 스냅/코디 리스트 페이지로 이동했습니다.")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li.style-list-item img.style-list-thumbnail__img'))
            )
            print("[스크래퍼] 코디 아이템 이미지가 로드될 때까지 대기했습니다.")
        except Exception as e:
            print(f"[스크래퍼] 코디 아이템 이미지 로딩 대기 중 오류 발생: {e}")
            time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        snap_items = soup.select('li.style-list-item')

        if not snap_items:
            print("[스크래퍼] 랜덤 코디 아이템을 찾을 수 없습니다.")
            return None

        print(f"[스크래퍼] 총 {len(snap_items)}개의 랜덤 코디 아이템을 찾았습니다.")
        selected_item = random.choice(snap_items)

        image_element = selected_item.select_one('img.style-list-thumbnail__img')
        image_url = 'N/A'
        if image_element:
            if 'data-original' in image_element.attrs and image_element['data-original']:
                image_url = image_element['data-original']
            elif 'src' in image_element.attrs and image_element['src']:
                image_url = image_element['src']

        link_element = selected_item.select_one('a.style-list-item__link')
        full_link = 'N/A'
        if link_element:
            onclick_attr = link_element.get('onclick', '')
            match = re.search(r"goView\('(\d+)'\)", onclick_attr)
            if match:
                item_id = match.group(1)
                full_link = f"https://www.musinsa.com/app/styles/detail/{item_id}"
            else:
                if link_element.get('href') and not link_element.get('href').startswith('javascript'):
                     full_link = link_element.get('href')

        # URL 정규화
        if image_url != 'N/A' and image_url.startswith('//'): image_url = 'https:' + image_url
        if image_url != 'N/A' and not re.match(r'https?://', image_url) and not image_url.startswith('data:image'):
            if image_url.startswith('/images/'): image_url = 'https://image.musinsa.com' + image_url
            else: image_url = 'https://www.musinsa.com' + image_url

        random_coordi = {'image_url': image_url, 'link': full_link}
        print(f"[스크래퍼] 랜덤 코디 아이템 1개를 선택했습니다.")

    except Exception as e:
        print(f"[스크래퍼] 랜덤 코디 스크래핑 중 오류가 발생했습니다: {type(e).__name__}: {e}")
        return None

    finally:
        if driver:
            driver.quit()
            print("[스크래퍼] 브라우저가 닫혔습니다.")
        return random_coordi


# --- Flask 라우트 정의 ---
@app.route('/')
def index():
    return render_template('index.html', results=None, weather_info=None, error_message=None)

@app.route('/weather_coordi', methods=['POST'])
def weather_coordi():
    city = request.form.get('city')
    if not city:
        return render_template('index.html', error_message="지역명을 입력해야 합니다.")

    weather_info = get_weather_info_and_keywords(city)
    if weather_info:
        results = scrape_musinsa_coordi(weather_info['search_keyword'], num_results=10)
        if results:
            return render_template('index.html', weather_info=weather_info, results=results)
        else:
            return render_template('index.html', error_message="코디를 가져오는 데 실패했습니다.", weather_info=weather_info) # 날씨 정보는 표시
    else:
        return render_template('index.html', error_message="날씨 정보를 가져오는 데 실패했습니다. 지역명을 확인하거나 API 키 설정을 확인해주세요.")

@app.route('/weather_random_coordi', methods=['POST'])
def weather_random_coordi():
    city = request.form.get('city')
    if not city:
        return render_template('index.html', error_message="지역명을 입력해야 합니다.")

    weather_info = get_weather_info_and_keywords(city)
    if weather_info:
        results = scrape_musinsa_coordi(weather_info['search_keyword'], num_results=1) # 1개만
        if results:
            return render_template('index.html', weather_info=weather_info, results=results)
        else:
            return render_template('index.html', error_message="랜덤 코디를 가져오는 데 실패했습니다.", weather_info=weather_info)
    else:
        return render_template('index.html', error_message="날씨 정보를 가져오는 데 실패했습니다. 지역명을 확인하거나 API 키 설정을 확인해주세요.")

@app.route('/keyword_coordi', methods=['POST'])
def keyword_coordi():
    keyword = request.form.get('keyword')
    if not keyword:
        return render_template('index.html', error_message="키워드를 입력해야 합니다.")

    results = scrape_musinsa_coordi(keyword, num_results=10)
    if results:
        return render_template('index.html', results=results)
    else:
        return render_template('index.html', error_message="코디를 가져오는 데 실패했습니다.")

@app.route('/keyword_random_coordi', methods=['POST'])
def keyword_random_coordi():
    keyword = request.form.get('keyword')
    if not keyword:
        return render_template('index.html', error_message="키워드를 입력해야 합니다.")

    results = scrape_musinsa_coordi(keyword, num_results=1) # 1개만
    if results:
        return render_template('index.html', results=results)
    else:
        return render_template('index.html', error_message="랜덤 코디를 가져오는 데 실패했습니다.")

@app.route('/random_coordi', methods=['POST'])
def random_coordi():
    random_item = scrape_random_coordi_item()
    if random_item:
        return render_template('index.html', results=[random_item]) # results는 리스트여야 하므로 [random_item]
    else:
        return render_template('index.html', error_message="랜덤 코디를 가져오는 데 실패했습니다.")