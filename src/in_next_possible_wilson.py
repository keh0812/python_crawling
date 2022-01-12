import os
import json
import time
import re
import logging
import configparser
import ssl

from datetime import datetime
from selenium import webdriver
from urllib import parse
from urllib.parse import urlsplit
from dateutil.parser import parse as datparse

from crawling_utils import CrawlingUtils


ssl._create_default_https_context = ssl._create_unverified_context

crawling_svc = CrawlingUtils()

# 설정파일 읽기
config = configparser.ConfigParser()    
config.read('../config.ini', encoding='utf-8') 

env = config['system']['env']
korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')

# 수집 날짜 범위
start_str = "20211031000000"
end_str = "20110101000000"

# 로그 세팅
def create_log(crawling_type, log_biz, log_msg):

    # 로그 정보
    log_data = {
        "log_time" : datetime.now().strftime('%Y%m%d%H%M%S'),
        "log_level" : config['logging']['log_level'],
        "log_prog" : crawling_type,
        "log_method" : "crawling_main()",
        "log_sys" : "crawling",
        "log_biz" : log_biz,
        "log_msg" : log_msg,
        "create_date" : datetime.now().strftime('%Y%m%d%H%M%S')
    }

    # 로그 저장 날짜 정보
    now_yyyy = datetime.now().strftime('%Y')
    now_mm = datetime.now().strftime('%m')
    now_dd = datetime.now().strftime('%d')

    # 로그 (json) 저장
    save_path = os.path.join(config['logging']['log_path'], now_yyyy, now_mm, now_dd)
    os.makedirs(save_path, exist_ok=True)
    log_file_name = crawling_type + "_" + datetime.now().strftime('%Y%m%d%H%M%S') + ".log"
    log_file_path = os.path.join(save_path, log_file_name)
    with open(log_file_path, "w", encoding='UTF-8') as json_file:

        json.dump(log_data, json_file, ensure_ascii=False)

    if env == "PRD":

        # sfrp 전송
        remote_path = config['ftp']['log_path']
        crawling_svc.ssh_client(log_file_path, os.path.join(remote_path, log_file_name))


# 로그 세팅
def log_setting():

    # 로그 생성
    logger = logging.getLogger()

    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)

    # log 출력 형식
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log 저장 날짜 정보
    now_yyyy = datetime.now().strftime('%Y')
    now_mm = datetime.now().strftime('%m')
    now_dd = datetime.now().strftime('%d')

    log_dir = os.path.join('../log/')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, now_yyyy + now_mm + now_dd + '.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def clean_text(text):
    cleaned_text = re.sub('[\{\}\[\]\;:|~`^\<>@\#\/\\\'\"]','', text)
    cleaned_text = re.sub('\t','', cleaned_text)
    cleaned_text = re.sub('\n','', cleaned_text)
    cleaned_text = re.sub('\&nbsp;  |  &nbsp;  |  \n | \t | \r','',cleaned_text)

    return cleaned_text

def clean_date(date_str, s_cd):
        
    # 특정 매체 보정 1202
    if s_cd == "1202":
        date_str = date_str.replace("." , "")
        now_yyyy = datetime.now().strftime('%Y')
        date_str = now_yyyy + date_str

    # 특정 매체 보정 3402
    if s_cd == "3402" and "•" in date_str:
        date_str = date_str.split('•')[0]

    # 특정 매체 보정 2302
    if s_cd == "2302" and "~" in date_str:
        date_str = date_str.split('~')[1]

    # 특정 매체 보정 2101
    if s_cd == "2101" and "~" in date_str:
        date_str = date_str.split('~')[1]

    # 특정 매체 보정 2203
    if s_cd == "2203" and "|" in date_str:
        date_str = date_str.split('|')[0]

    # 특정 매체 보정 3107
    if s_cd == "3107" and "|" in date_str:
        date_str = date_str.split('|')[0]
    
    # 특정 매체 보정 3106
    if s_cd == "3106" and "|" in date_str:
        date_str = date_str.split('|')[1]

    # 한글 삭제
    parseDate= re.sub(korean, '', date_str)

    # 특수문자 삭제
    parseDate= re.sub('[\{\}\[\]\;:|~`^\<>@\#\/\\\'\"]','', parseDate)
    parseDate = parseDate.strip('》 《')
    parseDate = parseDate.strip('《》')
    parseDate = parseDate.replace("[" , "")
    parseDate = parseDate.replace("]" , "")
    parseDate = parseDate.replace(")" , "")
    parseDate = parseDate.replace("(" , "")
    parseDate = parseDate.replace("," , "")
    parseDate = parseDate.replace("-" , "")
    parseDate = parseDate.replace(":" , "")

    if "ago" in parseDate:
        parseDate = datetime.now().strftime('%Y%m%d%H%M%S')

    try:
        dt = datparse(parseDate)
        cleaned_date = datetime.strftime(dt.date(), '%Y%m%d%H%M%S')

    except Exception as e:
        cleaned_date = parseDate

    return cleaned_date


class CrawlingPagingMain():

    def __init__(self):

        # 크롬 드라이버 설정
        self.driver_path = '../chromedriver/chromedriver.exe'

        self.options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--single-process')
        # options.add_argument('--disable-dev-shm-usage')
        prefs = {"download.default_directory" : config['chromedriver']['download_path']}
        self.options.add_experimental_option("prefs", prefs)

        self.logger = log_setting()


    # crawling template
    def crawling_main(self, collection_data):

        # try:

            # 대분류 코드
            l_cd = collection_data["l_cd"]
            # 중분류 코드
            m_cd = collection_data["m_cd"]
            # 소분류 코드
            s_cd = collection_data["s_cd"]
            # 메뉴 코드
            menu_cd = collection_data["menu_cd"]
            # 수집주기 코드
            crawling_type = collection_data["cycle_cd"]
            # 템플릿 코드
            template_code = collection_data["template_cd"]

            # 로그 세팅
            logger = self.logger

            # 크롬 드라이버 실행
            default_directory = os.path.join(config['chromedriver']['download_path'], crawling_type)
            prefs = {"download.default_directory" : default_directory}
            self.options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(self.driver_path, chrome_options = self.options)

            # 페이지 로딩 최대 30초 대기
            driver.implicitly_wait(30)

            # 수집대상 정보 읽기
            data_path = os.path.join("../target_data", l_cd, m_cd)
            data_name = os.path.join(data_path, l_cd + '_' + m_cd + '_' + s_cd + '_' + menu_cd + '.json')   

            target_file = open(data_name, 'rt', encoding='UTF8')

            # crawling target JSON object as 
            target_data = json.load(target_file)

            # Closing file
            target_file.close()

            # 수집 대상 정보
            common_data = target_data['common_data']

            # 수집 메타 정보
            meta_data = target_data['meta_data']

            # 이벤트 정보
            event_data = target_data['event_data']

            # 페이징 정보
            paging_data = target_data['paging_data']

            # 결과 저장 날짜 정보
            now_yyyy = datetime.now().strftime('%Y')
            now_mm = datetime.now().strftime('%m')
            now_dd = datetime.now().strftime('%d')

            # 크롤링 대상 기본 정보
            identifier = common_data['identifier']
            m_cd_name = common_data['m_cd_name']
            s_cd_name = common_data['s_cd_name']
            menu_name = common_data['menu_name']

            crawling_svc.common_info(common_data)

            # 저장 경로 생성
            # /datalake/nams/media/pynews/military/2021/07/13/001/txt/meta.json
            # save_path = os.path.join(config['crawling']['save_path'], l_cd, m_cd, s_cd, menu_cd, now_yyyy, now_mm, now_dd)
            # os.makedirs(save_path, exist_ok=True)

            # 게시물 상세페이지 링크
            detail_tag = common_data['detail_tag']
            event_date = common_data['event_date'] 

            # 로그인 유무 체크
            if 'login' in event_data:

                crawling_svc.login(driver, event_data)
                logger.info(f' | crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | 로그인')  

            # URL 링크 이동
            target_url = common_data['url']
            driver.get(target_url)

            # 브라우저창 최대 사이즈
            driver.maximize_window()

            # 해더 영역 사이즈 보정
            headless_height = 0
            if 'headless' in event_data:

                headless_height += 200

                headless_tag = event_data['headless']

                headless = driver.find_element_by_css_selector(headless_tag)
                headless_height = headless_height + headless.size['height']
            
            headless_height = str(headless_height)

            # 메뉴 이동
            if 'menu' in event_data:

                menu_list = event_data['menu']

                for menu_tag in menu_list:

                    menu_btn = driver.find_element_by_xpath(menu_tag)
                    menu_btn.click()
                    time.sleep(5)

            # 키워드 검색
            if 'search' in event_data:

                crawling_svc.keyword_search(driver, event_data)
                time.sleep(5)

            logger.info(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | 크롤링 시작')
            create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, "크롤링 시작")

            # 페이징 정보
            next_tag = paging_data['next_tag']

            # 페이지 카운트 초기 설정
            paging_cnt = 1

            # 다음 페이지 유무 체크
            next_exists = True

            while next_exists:

                    # 페이징 요소 확인
                    last_next = driver.find_element_by_css_selector(next_tag).get_attribute('data-disabled')
                    paging_num = paging_cnt
                
                    logger.info(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | {paging_num} 페이지')
                    create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, str(paging_num) + " 페이지")

                    # 상세페이지 이동
                    if (detail_tag != ""):

                        # 상세 페이지 요소 확인
                        items = driver.find_elements_by_css_selector(detail_tag)
                        item_cnt = len(items)
                        success_cnt = 0

                        logger.info(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | 크롤링 대상 : {item_cnt} 건')
                        create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, "크롤링 대상 : " + str(item_cnt) + " 건")

                        # 상세페이지 메타정보 추출
                        for i in range (item_cnt):

                            # 결과 저장경로
                            save_path = os.path.join(config['crawling']['save_path'], l_cd, m_cd, s_cd, menu_cd, now_yyyy, now_mm, now_dd)

                            # 등록일 임시저장
                            event_date_text = ""

                            if event_date != "":
                                event_date_items = driver.find_elements_by_css_selector(event_date)

                                driver.execute_script("arguments[0].scrollIntoView(true);", event_date_items[i])
                                if headless_height != "0":
                                    driver.execute_script("window.scrollTo(0, window.scrollY - " + headless_height + ");")
                                    time.sleep(2)

                                event_date_text = clean_date(event_date_items[i].text, s_cd)

                                # 수집날짜 비교
                                if event_date_text != "":
                                    
                                    # 저장경로 수정
                                    save_path = os.path.join(config['crawling']['save_path'], l_cd, m_cd, s_cd, menu_cd, event_date_text[0:4], event_date_text[4:6], event_date_text[6:8])
                                    
                                    _start_time = datetime.strptime(start_str, '%Y%m%d%H%M%S')
                                    _end_time = datetime.strptime(end_str, '%Y%m%d%H%M%S')
                                    _event_time = datetime.strptime(event_date_text, '%Y%m%d%H%M%S')

                                    if (_start_time < _event_time):
                                        print('continue !!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                        continue
                                    if (_end_time > _event_time):
                                        print('break !!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                        break

                            # 결과 저장경로
                            os.makedirs(save_path, exist_ok=True)
                            
                            if env == "PRD":

                                offset_list = []

                                # 옵셋 세팅
                                # offset JSON file
                                offset_dir = os.path.join('../offset/')
                                os.makedirs(offset_dir, exist_ok=True)
                                offset_file_dir = os.path.join(offset_dir,  l_cd + "_" + m_cd + "_" + s_cd + "_" + menu_cd + '.json')

                                # 파일 유무 확인
                                if os.path.isfile(offset_file_dir):
                                    offset_file = open(offset_file_dir, "rt", encoding='UTF8')
                                    offset_list = json.load(offset_file)

                            # 파일 카운트
                            file_cnt = 1
                            
                            # 파일 리스트
                            file_list = []

                            # 광고 제거
                            if 'advert' in event_data:

                                try:

                                    advert_close = driver.find_element_by_css_selector(event_data['advert']['advert_close'])
                                    advert_close.click()
                                    time.sleep(2)  

                                except Exception as e:

                                    print('no advert')
                            

                            # 상세페이지 기본 타입
                            if "detail" == template_code:
                                
                                # 상세 페이지 요소 확인
                                items = driver.find_elements_by_css_selector(detail_tag)

                            # 요소까지 스크롤 다운
                            # somthing element 까지 스크롤
                            # action = ActionChains(driver)
                            # action.move_to_element(items[i]).perform()
                            # 특정 요소가 보일 때까지 스크롤다운 하기 (by the visibility of the element)
                            driver.execute_script("arguments[0].scrollIntoView(true);", items[i])
                            time.sleep(100)

                            # 식별자 초기화
                            data_id = str(i)

                            # 자바스크립트 타입 식별자
                            if 'javascript' in event_data:
                                javascript_tag = event_data['javascript']
                                javascript_id = items[i].get_attribute(javascript_tag)
                                data_id = re.sub(r'[^0-9]', '', javascript_id)

                            if headless_height != "0":
                                driver.execute_script("window.scrollTo(0, window.scrollY - " + headless_height + ");")
                                time.sleep(2)

                            # window open 타입
                            if "window_open" == template_code:

                                window_open_href = items[i].get_attribute('href')

                                #open new tab with specific url
                                driver.execute_script("window.open('" + window_open_href +"');")
                                #hadle new tab
                                second_tab = driver.window_handles[1]
                                #switch to second tab
                                driver.switch_to.window(second_tab)

                                detail_url = window_open_href

                            # 새탭 타입
                            if "new" == template_code:
                                items[i].click()
                                time.sleep(2)
                                #최근 열린 탭으로 전환
                                driver.switch_to.window(driver.window_handles[-1])

                                # 상세페이지 url
                                detail_url = driver.current_url

                            # 모달 타입
                            elif 'modal' == template_code:
                                # 모달 클릭
                                items[i].click()
                                
                            # 상세페이지 없는 타입
                            elif "none" == template_code:
                                pass

                            # 상세페이지 기본 타입
                            elif "detail" == template_code:

                                # 상세 페이지 요소 확인
                                items = driver.find_elements_by_css_selector(detail_tag)

                                # URL 필터링 처리
                                if "url_filtering" in event_data:
                                    tmp_href = items[i].get_attribute('href')
                                    org_components = urlsplit(target_url)
                                    new_components = urlsplit(tmp_href)
                                    detail_url = org_components.scheme + '://' + org_components.netloc + org_components.path + '?' + new_components.query

                                    driver.get(detail_url)

                                else:
                                    time.sleep(10)
                                    # 상세페이지 이동
                                    items[i].click()
                                    time.sleep(2)

                                    # 상세페이지 url
                                    detail_url = driver.current_url

                            # 상세 페이지 URL 추출
                            link_url = driver.current_url
                            parse_url = parse.urlparse(link_url)
                            parse_query = parse.parse_qs(parse_url.query)

                            # 식별자 유무 확인
                            # try:

                            if identifier != "":

                                # 게시글 아이디 추출
                                data_id = parse_query[identifier][0]

                            if 'identifier' in event_data:

                                # 모달 식별자 처리
                                if 'modal' in event_data:

                                    modal_identifier = event_data['modal']['identifier']
                                    link_url = items[i].get_attribute(modal_identifier)

                                    # 로딩 기다리기
                                    time.sleep(5)

                                # 상세페이지 없는 타입
                                if 'none' in event_data:

                                    time.sleep(2)
                                    # 상세 페이지 없는 타입의 식별자는 특정 태그의 속성값을 참고하여 생성
                                    none_identifier_tag = event_data['none']['identifier_tag']
                                    none_identifier = event_data['none']['identifier']

                                    if none_identifier_tag in meta_data:
                                        link_url = items[i].find_element_by_css_selector(meta_data[none_identifier_tag]).get_attribute(none_identifier)
                                    else:
                                        link_url = items[i].find_element_by_css_selector(none_identifier_tag).get_attribute(none_identifier)

                                    # 게시글 아이디 추출
                                    # none_identifier = event_data['none']['identifier']
                                    # parse_url = parse.urlparse(link_url)
                                    # parse_query = parse.parse_qs(parse_url.query)
                                    # data_id = parse_query[none_identifier][0]

                                # CrawlingUtils 게시글 아이디 생성 함수 호출
                                data_id = crawling_svc.get_identifier(event_data["identifier"], link_url, data_id)

                            # except:

                            #     # 게시글 생성 실패 시 index로 게시글 아이디 생성
                            #     data_id = str(i)

                            # finally:

                            data_id = data_id[:30]

                            print('data_id == ', l_cd + '_' + m_cd + '_' + s_cd + '_' + menu_cd + ' == ' + str(i) + '/' + str(item_cnt) + " == "+  data_id)

                            if env == "PRD":
                                # 크롤링 페이지 offset 비교
                                if data_id in offset_list: 
                                    break

                            # 추출 결과 파일 meta.json 데이터 세팅
                            result_data = {}

                            # 도큐먼트 ID
                            doc_id = s_cd + "_" + menu_cd + "_" + data_id
                            result_data['id'] = "nams_" + doc_id
                            # 업무구분 대분류 코드
                            result_data['biz_l_cd'] = ""
                            # 업무구분 중분류 코드
                            result_data['biz_m_cd'] = ""
                            # 업무구분 소분류 코드
                            result_data['biz_s_cd'] = ""
                            # 데이터출처 대분류 코드
                            result_data['data_src_l_cd'] = l_cd
                            # 데이터출처 중분류 코드
                            result_data['data_src_m_cd'] = m_cd
                            # 데이터출처 소분류 코드
                            result_data['data_src_s_cd'] = s_cd
                            # 메뉴 아이디
                            result_data['menu_id'] = menu_cd
                            # 자료유형 대분류 코드
                            result_data['data_type_l_cd'] = "B001"
                            # 자료유형 중분류 코드
                            result_data['data_type_m_cd'] = "203"
                            # 보안등급 분류 코드
                            result_data['sec_cd'] = "5"
                            # 참고 URL
                            result_data['url'] = link_url
                            # 수집일자
                            # result_data['col_dt'] = datetime.now().strftime('%Y%m%d%H%M%S')
                            # 부가정보
                            result_data['etc'] = ""

                            # 첨부파일 정보
                            result_data['attach_file'] = []

                            # 도큐먼트 내용
                            result_data['content'] = ""

                            # 도큐먼트 제목
                            result_data['title'] = ""

                            # 게시글 등록일자
                            result_data['event_date'] = ""
                            if event_date_text != "":
                                result_data['event_date'] =  clean_date(event_date_text, s_cd)

                            # 작성자
                            result_data['author'] = ""

                            # 메타정보 리스트
                            meta_list = meta_data.keys()

                             # 메타정보 순서 변경
                            print('메타정보 순서 변경')
                            meta_list = list(meta_list)
                            meta_list.remove('write_date_tag')
                            meta_list.insert(0, 'write_date_tag')
                            print('meta_list = ', meta_list)

                            for tag in meta_list:
                                
                                # 요소 높이 초기화
                                driver.execute_script("window.scrollTo(0, 0)")
                                time.sleep(2)

                                # 메타 정보 유무 확인
                                if meta_data[tag] != "":

                                    if "none" == template_code:
                                        data_obj = items[i].find_elements_by_css_selector(meta_data[tag])

                                    else:
                                        data_obj = driver.find_elements_by_css_selector(meta_data[tag])

                                    # 데이터 요소 유무 확인
                                    if(data_obj):

                                        # 등록일 타입 데이터 추출
                                        if tag == 'write_date_tag':
                                            
                                            # 문자열 타입 데이터 추출 함수 호출
                                            str_extraction_data = crawling_svc.str_extraction(driver, data_obj, headless_height)

                                            # 게시글 등록일자
                                            if (event_date_text == ""):
                                                event_date_text = clean_date(str_extraction_data, s_cd)
                                                result_data['event_date'] = event_date_text

                                                # 결과 저장경로
                                                save_path = os.path.join(config['crawling']['save_path'], l_cd, m_cd, s_cd, menu_cd, event_date_text[0:4], event_date_text[4:6], event_date_text[6:8])
                                                os.makedirs(save_path, exist_ok=True)

                                                # 수집날짜 비교
                                                _start_time = datetime.strptime(start_str, '%Y%m%d%H%M%S')
                                                _end_time = datetime.strptime(end_str, '%Y%m%d%H%M%S')
                                                _event_time = datetime.strptime(event_date_text, '%Y%m%d%H%M%S')
                                                
                                                _break_check = False
                                                _break_type = None

                                                if (_start_time < _event_time):
                                                    print('continue !!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                                    _break_check = True
                                                    _break_type = "continue"
                                                if (_end_time > _event_time):
                                                    print('break !!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                                                    _break_check = True
                                                    _break_type = "break"

                                                if _break_check:

                                                    # 템플릿 코드 별 뒤로가기 처리
                                                    # 새탭 타입
                                                    if "new" == template_code or "window_open" == template_code:
                                                        # if len(driver.window_handles) == 2:   

                                                        #최근 열린 탭으로 전환
                                                        driver.switch_to.window(driver.window_handles[-1])

                                                        # 창 닫기
                                                        driver.close()
                                                        #다시 맨 처음 탭으로 변경
                                                        driver.switch_to.window(driver.window_handles[0])

                                                    # 모달 타입
                                                    elif 'modal' == template_code:
                                                        close_tag = event_data['modal']['close_tag']

                                                        close_btn = driver.find_element_by_css_selector(close_tag)
                                                        close_btn.click()

                                                    # 상세페이지 없는 타입
                                                    elif "none" == template_code:

                                                        pass

                                                    # 상세페이지 기본 타입
                                                    elif "detail" == template_code:

                                                        # 다운로드 후 URL 변조 여부 체크
                                                        tmp_url = driver.current_url
                                                        if detail_url != tmp_url:
                                                            # 뒤로가기
                                                            driver.back()

                                                        # 뒤로가기
                                                        driver.back()

                                                    if _break_type == "continue":
                                                        continue
                                                    if _break_type == "break":
                                                        break

                                        # 이미지 타입 데이터 추출
                                        if tag == 'img_tag':
                                            
                                            file_list, file_cnt = crawling_svc.img_extraction(data_obj, save_path, data_id, file_cnt, file_list)

                                            # 첨부파일 정보
                                            result_data['attach_file'] = (file_list)
                                        
                                        # 첨부파일 타입 데이터 추출
                                        if tag == 'download_tag':

                                            file_list, file_cnt = crawling_svc.file_extraction(driver, data_obj, l_cd, m_cd, s_cd, save_path, data_id, file_cnt, file_list, headless_height, crawling_type)

                                            # 첨부파일 정보
                                            result_data['attach_file'] = (file_list)
                                        
                                        # 본문내용 타입 데이터 추출
                                        if tag == 'contents_tag':

                                            contents_data = crawling_svc.contents_extraction(driver, data_obj, event_data, headless_height)

                                            # 도큐먼트 내용
                                            result_data['content'] = clean_text(contents_data)
                                        
                                        # 본문제목 데이터 추출
                                        if tag == 'title_tag':
                                            
                                            # 문자열 타입 데이터 추출 함수 호출
                                            str_extraction_data = crawling_svc.str_extraction(driver, data_obj, headless_height)

                                            # 도큐먼트 제목
                                            result_data['title'] = clean_text(str_extraction_data)
                                        
                                        # 등록자 타입 데이터 추출
                                        if tag == 'author_tag':
                                            
                                            # 문자열 타입 데이터 추출 함수 호출
                                            str_extraction_data = crawling_svc.str_extraction(driver, data_obj, headless_height)

                                            # 작성자
                                            result_data['author'] = clean_text(str_extraction_data)


                                # 추출 대상이 없는 경우
                                else:
                                    
                                    pass

                            # 추출 데이터 출력
                            print('result_data == ', result_data)

                            # 추출 결과 저장 경로
                            crawling_path = os.path.join(save_path, data_id, "txt")
                            os.makedirs(crawling_path, exist_ok=True)

                            # # html 저장
                            # html = driver.page_source
                            # html_file_path = os.path.join(crawling_path, "html.html")
                            # with open(html_file_path, 'w',encoding='UTF-8') as html_f:
                            #     html_f.write(html)

                            # 추출 결과(json) 저장
                            meta_file_path = os.path.join(crawling_path, "meta.json")
                            with open(meta_file_path, "w", encoding='UTF-8') as json_file:

                                json.dump(result_data, json_file, ensure_ascii = False, indent = 4)

                            # 크룔링 결과 압축 경로
                            result_path = os.path.join(save_path, data_id) 

                            # 크롤링 결과 저장
                            if event_date_text == "":
                                event_date_text = datetime.now().strftime('%Y%m%d%H%M%S')
                            crawling_svc.send_results(result_path, l_cd, m_cd, s_cd, menu_cd, data_id, crawling_type, event_date_text)

                            if env != "LOCAL":
                                # 크롤링 페이지 offset 저장
                                offset_list.append(data_id)

                                # 크롤링 페이지 offset 저장
                                with open(offset_file_dir, 'w', encoding='utf-8') as json_file:

                                    json.dump(offset_list, json_file, ensure_ascii=False)

                            success_cnt += 1
                            
                            # 새탭 타입
                            if "new" == template_code or "window_open" == template_code:
                                # if len(driver.window_handles) == 2:   

                                #최근 열린 탭으로 전환
                                driver.switch_to.window(driver.window_handles[-1])

                                # 창 닫기
                                driver.close()
                                #다시 맨 처음 탭으로 변경
                                driver.switch_to.window(driver.window_handles[0])

                            # 모달 타입
                            elif 'modal' == template_code:
                                close_tag = event_data['modal']['close_tag']

                                close_btn = driver.find_element_by_css_selector(close_tag)
                                close_btn.click()

                            # 상세페이지 없는 타입
                            elif "none" == template_code:

                                pass

                            # 상세페이지 기본 타입
                            elif "detail" == template_code:

                                # 다운로드 후 URL 변조 여부 체크
                                tmp_url = driver.current_url
                                if detail_url != tmp_url:
                                    # 뒤로가기
                                    driver.back()

                                # 뒤로가기
                                driver.back()


                        logger.info(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | 크롤링 성공 : {success_cnt} 건')
                        create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, "크롤링 성공 : " + str(success_cnt) + " 건")

                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(30)

                    if last_next != "true":
                        time.sleep(200)
                        driver.find_element_by_css_selector(next_tag).click()
                        paging_cnt = paging_cnt + 1
                        print("<<<< 다음 페이지로 이동 >>>>")
                        time.sleep(30)
                    else:
                        print("<<<< 마지막 페이지 >>>>")
                        next_exists = False

            # driver 닫기
            driver.close()
            driver.quit()
            
            logger.info(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | 크롤링 종료')
            create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, "크롤링 종료")

        # except Exception as e:

        #     # driver 닫기
        #     if driver:
        #         driver.close()
        #         driver.quit()

        #     e_type = type(e).__name__

        #     if e_type == "FileNotFoundError":
        #         logger.error(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | Exception FileNotFoundError')
        #         create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, "Exception FileNotFoundError")

        #     else:

        #         e_str = str(e)

        #         split_str = e_str.splitlines()
        #         join_str = "".join(split_str)

        #         logger.error(f'crawling | crawling_main() | crawling | {l_cd}/{m_cd}/{s_cd}/{menu_cd} | Exception {join_str}')
        #         create_log(crawling_type, l_cd + "/" + m_cd + "/" + s_cd + "/" + menu_cd, "Exception " + join_str)

