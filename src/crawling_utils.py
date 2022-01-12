import os
import requests
import shutil
import time
import mimetypes
import zipfile
import paramiko
import configparser
import ssl
import re
import urllib.request
import cgi

from urllib.request import urlopen
from urllib.request import urlretrieve
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

# 설정파일 읽기
config = configparser.ConfigParser()    
config.read('../config.ini', encoding='utf-8') 

env = config['system']['env']

# 파일 확장자 체크
file_check = ['do']


class CrawlingUtils():

    # 파일 다운로드 requests 타입 체크
    def check_download_type(self, l_cd, m_cd, s_cd):

        # if not (l_cd == "C002" and  m_cd == "03" and  s_cd == "003") and not (l_cd == "C002" and  m_cd == "03" and  s_cd == "002") and not (l_cd == "C002" and  m_cd == "01" and  s_cd == "001") and not (l_cd == "C002" and  m_cd == "03" and  s_cd == "005") and not (l_cd == "C003" and  m_cd == "04" and  s_cd == "003"):
        # if not (l_cd == "C002" and  m_cd == "006" and  s_cd == "052") and not (l_cd == "C002" and  m_cd == "006" and  s_cd == "051") and not (l_cd == "C002" and  m_cd == "004" and  s_cd == "020") and not (l_cd == "C002" and  m_cd == "006" and  s_cd == "054") and not (l_cd == "C003" and  m_cd == "010" and  s_cd == "073"):
        if not (l_cd == "C002" and  m_cd == "203" and  s_cd == "2303") and not (l_cd == "C002" and  m_cd == "203" and  s_cd == "2302") and not (l_cd == "C002" and  m_cd == "201" and  s_cd == "2101") and not (l_cd == "C002" and  m_cd == "203" and  s_cd == "2305") and not (l_cd == "C003" and  m_cd == "304" and  s_cd == "3403"):

            return True
        else:
            return False

    # 크롤링 common_data 정보 출력
    def common_info(self, common_data):

        l_cd = common_data['l_cd']
        l_cd_name = common_data['l_cd_name']
        m_cd = common_data['m_cd']
        m_cd_name = common_data['m_cd_name']
        s_cd = common_data['s_cd']
        s_cd_name = common_data['s_cd_name']
        menu_cd = common_data['menu_cd']
        menu_name = common_data['menu_name']

        info_data = {
            "l_cd" : l_cd,
            "l_cd_name" : l_cd_name,
            "m_cd" : m_cd,
            "m_cd_name" : m_cd_name,
            "s_cd" : s_cd,
            "s_cd_name" : s_cd_name,
            "menu_cd" : menu_cd,
            "menu_name" : menu_name,
        }

        print(info_data)


    # 파일 다운로드 대기
    def download_wait(self, path_to_downloads):
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < 600:
            time.sleep(1)
            dl_wait = False
            for fname in os.listdir(path_to_downloads):
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
            print('download_wait == ', seconds)

        time.sleep(5)


    # sfrp 전송
    def ssh_client(self, file_path, remote_path):
        print("ssh connect")
        
        host = config['ftp']['host']
        username = config['ftp']['username']
        password = config['ftp']['password']
        port = config['ftp']['port']

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, port=port) 
        sftp = ssh.open_sftp()
        print("send start")

        sftp.put(file_path, remote_path)
        print("sfpt put")
        

    # 키워드 검색
    def keyword_search(self, driver, event_data):

        search_input = event_data["search"]["search_input"]
        search_keyword = event_data["search"]["search_keyword"]
        # search_input2 = event_data["search"]["search_input2"]
        # search_keyword2 = event_data["search"]["search_keyword2"]
        search_btn = event_data["search"]["search_btn"]

        # 검색 키워드 입력 후 검색버튼 클릭
        driver.find_element_by_css_selector(search_input).send_keys(search_keyword)
        # driver.find_element_by_css_selector(search_input2).send_keys(search_keyword2)
        driver.find_element_by_css_selector(search_btn).click()


    # 로그인
    def login(self, driver, event_data):

        login_url = event_data["login"]["url"]
        id = event_data["login"]["id"]
        pw = event_data["login"]["pw"]
        id_input = event_data["login"]["id_input"]
        pw_input = event_data["login"]["pw_input"]
        event_next = event_data["login"]["event_next"]
        event_signin = event_data["login"]["event_signin"]
        event = event_data["login"]["event"]

        #아이디 입력 후 다음버튼 없을 시
        if (event == "signin"):
            # 로그인 화면 이동
            driver.get(login_url)

            # id 입력 후 다음
            driver.find_element_by_css_selector(id_input).send_keys(id)

            # pw 입력 후 로그인 
            driver.find_element_by_css_selector(pw_input).send_keys(pw)
            driver.find_element_by_css_selector(event_signin).click()

        #아이디 입력 후 다음버튼 있을 시
        elif (event == "next_signin"):
            # 로그인 화면 이동
            driver.get(login_url)

            # id 입력 후 다음
            driver.find_element_by_css_selector(id_input).send_keys(id)
            driver.find_element_by_css_selector(event_next).click()

            # pw 입력 후 로그인 
            driver.find_element_by_css_selector(pw_input).send_keys(pw)
            driver.find_element_by_css_selector(event_signin).click()


    # 게시글 아이디 추출
    def get_identifier(self, event_data, link_url, data_id):

        if (event_data == "slash_after1"):
            data_id = link_url.split('/')[-1]

        if (event_data == "slash_after2"):
            data_id = link_url.split('/')[-2]

        if (event_data == "slash_after3"):
            data_id = link_url.split('/')[-3]

        if (event_data == "ttmmdd"):
            data_id = link_url.split('/')[-1]
            data_dd = link_url.split('/')[-2]
            data_mm = link_url.split('/')[-3]
            data_yy = link_url.split('/')[-4]

            data_id = data_yy + data_mm + data_dd + data_id

        if (event_data == "reverse_40"):
            data_id = data_id[-40:]
			
        if (event_data == "kyungnam"):
            data_id = data_id[35:55]

        if (event_data == "url_pass"):
            data_id = link_url

        if (event_data == "remove_html"):

            url_split = str(link_url)

            url_split = url_split.split('/') # /로 나눔
            delete_1 = url_split[-1] # 식별자가 포함된 부분만 저장

            new_identifier_import = delete_1.split('.') # . 기준으로 뒷부분 제거
            new_identifier = new_identifier_import[0] # 식별자만 저장
            data_id = new_identifier
        
        if (event_data == "state"):
            first = link_url.split('/')[-2]
            data_id = first[15:-1]
            second = link_url.split('/')[-3]
            data_id2 = second[0:5]

            data_id = data_id + data_id2

        if (event_data == "contentsView"):

            data_id = link_url.replace("javascript:contentsView('", "").replace("')", "")

        if (event_data == "integer"):

            data_id = re.sub(r'[^0-9]', '', link_url)
        
        return data_id


    # 이미지 타입 데이터 추출
    def img_extraction(self, data_obj, save_path, data_id, file_cnt, file_list):

        for obj in data_obj:

            download_href = obj.get_attribute("src")

            # 확장자 찾기
            # r = requests.get(download_href)
            # extension = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0]) 

            # 저장 경로 생성
            download_path = os.path.join(save_path, data_id, 'img')
            os.makedirs(download_path, exist_ok=True)
            file_path = download_path + '/' + data_id + "_" + str(file_cnt) + '.jpg'

            time.sleep(20)
            urlretrieve(download_href, file_path)
            time.sleep(5)

            # 다운로드 대기
            self.download_wait(download_path)

            # 파일 용량
            file_size = os.path.getsize(file_path)

            file_real_path = os.path.join(download_path.replace(config['crawling']['replace_path'], ""), data_id + "_" + str(file_cnt) + '.jpg') 
            file_list.append(
                {   
                    "file_name": os.path.basename(download_href),
                    "file_id": data_id + "_" + str(file_cnt),
                    "file_path": file_real_path.replace('\\', '/'),
                    "file_size": str(file_size)
                }
            )

            file_cnt += 1

        return file_list, file_cnt
    

    # 첨부파일 타입 데이터 추출
    def file_extraction(self, driver, data_obj, l_cd, m_cd, s_cd, save_path, data_id, file_cnt, file_list, headless_height, crawling_type):

        # 파일 다운로드 후 특정 디렉토리로 이동
        for obj in data_obj:

            download_target= obj.get_attribute("target")

            # if (download_target == "_blank" and s_cd != "inss" and s_cd != "stepi" and s_cd != "unikorea" and s_cd != "krihs" and s_cd != "crs")    
            if (download_target == "_blank" and self.check_download_type(l_cd, m_cd, s_cd)):

                print('requests')

                download_href = obj.get_attribute("href")

                remotefile = urlopen(download_href)
                blah = remotefile.info()['Content-Disposition']

                # 파일 다운로드 비정상일경우 처리
                if blah != None:

                    # 확장자 찾기
                    if env == "PRD":
                        r = requests.get(download_href, verify=False)
                    else: 
                        r = requests.get(download_href, verify='C:/project/mou/key/prism-UNIKOR.crt')
                    
                    extension = mimetypes.guess_extension(r.headers.get('content-type', '').split(';')[0])

                    # 확장자별 디렉토리
                    ext_repl = extension.replace(".", "").lower()
                    ext_path = "doc"

                    if (ext_repl == "pdf"): 
                        ext_path = "pdf"  

                    if (ext_repl == "zip"):
                        ext_path = "zip"

                    if (ext_repl == "mp4"):
                        ext_path = "mp4"

                    if (ext_repl == "mp3"):
                        ext_path = "mp3"

                    if (ext_repl == "jpg" or ext_repl == "png"):
                        ext_path = "img"

                    # 저장 경로 생성
                    download_path = os.path.join(save_path, data_id, ext_path)
                    os.makedirs(download_path, exist_ok=True)
                    file_path = download_path + '/' + data_id + "_" + str(file_cnt) + extension

                    try:
                        urlretrieve(download_href, file_path)
                        time.sleep(2)

                    except Exception as e:
                        print('retry')
                        time.sleep(1000)
                        urlretrieve(download_href, file_path)

                    if ext_repl in file_check:

                        os.remove(file_path)

                    else:

                        # 파일 용량
                        file_size = os.path.getsize(file_path)

                        file_real_path = os.path.join(download_path.replace(config['crawling']['replace_path'], ""), data_id + "_" + str(file_cnt) + extension) 
                        file_list.append(
                            {   
                                "file_name": os.path.basename(download_href) + extension,
                                "file_id": data_id + "_" + str(file_cnt),
                                "file_path": file_real_path.replace('\\', '/'),
                                "file_size": str(file_size)
                            }
                        )

                        file_cnt += 1

            else:

                print('click')

                # 파일 다운로드 클릭 전 URL
                org_split_url = driver.current_url.split('?')[0]

                download_tmp_path = os.path.join(config['chromedriver']['download_path'], crawling_type)
                os.makedirs(download_tmp_path, exist_ok=True)

                driver.execute_script("arguments[0].scrollIntoView(true);", obj)
                
                if headless_height != "0":
                    driver.execute_script("window.scrollTo(0, window.scrollY - " + headless_height + ");")
                    time.sleep(2)

                obj.click()
                time.sleep(5)

                # 파일 다운로드 클릭 후 URL
                current_split_url = driver.current_url.split('?')[0]

                # 파일 다운로드 비정상일경우 처리
                # 파일 다운로드 클릭 이후 URL 비교
                if org_split_url == current_split_url:

                    # os.path.basename(filename) - 파일명만 추출
                    # os.path.splitext(filename) - 확장자와 나머지 분리
                    # filename, extension = os.path.splitext(filename)

                    # 다운로드 대기
                    self.download_wait(download_tmp_path)

                    time.sleep(2)
                    last_file = max([download_tmp_path + '\\' + f for f in os.listdir(download_tmp_path)], key=os.path.getctime)

                    file_path = os.path.basename(last_file)
                    file_name, extension = os.path.splitext(file_path)

                    if extension == ".crdownload":
                        print('re download_wait')
                        time.sleep(5)
                        self.download_wait(download_tmp_path)

                        time.sleep(2)
                        last_file = max([download_tmp_path + '\\' + f for f in os.listdir(download_tmp_path)], key=os.path.getctime)
                        file_path = os.path.basename(last_file)
                        file_name, extension = os.path.splitext(file_path)

                    # 확장자별 디렉토리
                    ext_repl = extension.replace(".", "").lower()
                    ext_path = "doc"

                    if (ext_repl == "pdf"): 
                        ext_path = "pdf"

                    if (ext_repl == "zip"):
                        ext_path = "zip"

                    if (ext_repl == "jpg" or ext_repl == "png" or ext_repl == "jpeg"):
                        ext_path = "img"

                    if (ext_repl == "mp4"):
                        ext_path = "mp4"

                    if (ext_repl == "mp3"):
                        ext_path = "mp3"

                    if ext_repl in file_check:

                        os.remove(last_file)

                    else:

                        # 저장 경로 생성
                        download_path = os.path.join(save_path, data_id, ext_path)
                        os.makedirs(download_path, exist_ok=True)

                        shutil.move(os.path.join(download_tmp_path, last_file), download_path)

                        file_path = os.path.join(download_path, data_id + "_" + str(file_cnt) + extension)
                        
                        # 이름 변경
                        time.sleep(5)
                        os.rename(os.path.join(download_path, file_name + extension), file_path)

                        # 파일 용량
                        file_size = os.path.getsize(file_path)

                        file_real_path = os.path.join(download_path.replace(config['crawling']['replace_path'], ""), data_id + "_" + str(file_cnt) + extension) 
                        # obj.text.replace('pdf\n','')
                        file_list.append(
                            {   
                                "file_name": os.path.join(file_name, extension).replace('\\', ''),
                                "file_id": data_id + "_" + str(file_cnt),
                                "file_path": file_real_path.replace('\\', '/'),
                                "file_size": str(file_size)
                            }
                        )

                        # 임시파일 삭제
                        shutil.rmtree(download_tmp_path)

                        file_cnt += 1

                else:
                
                    # 뒤로가기
                    driver.back()

        return file_list, file_cnt


    # 본문내용 타입 데이터 추출
    def contents_extraction(self, driver, data_obj, event_data, headless_height):

        data = ""

        # 본문 내용 탭 이동
        if 'tab' in event_data:
            event_tag = event_data["tab"]["tab_tag"]
            # 페이지 내 요소 개수 확인
            event_items = driver.find_elements_by_css_selector(event_tag)
            event_cnt = 0

        for obj in data_obj:
                
            # event_data 요소까지 스크롤 다운
            # somthing element 까지 스크롤
            # 본문 내용 탭 이동
            if 'tab' in event_data:
                event_items[event_cnt].click()
                event_cnt =+ 1

            # action = ActionChains(driver)
            # action.move_to_element(obj).perform()
            # 특정 요소가 보일 때까지 스크롤다운 하기 (by the visibility of the element)
            driver.execute_script("arguments[0].scrollIntoView(true);", obj)
            if headless_height != "0":
                driver.execute_script("window.scrollTo(0, window.scrollY - " + headless_height + ");")
                time.sleep(2)

            data += obj.text

        return data


    # 문자열 타입 데이터 추출
    def str_extraction(self, driver, data_obj, headless_height):
        
        data = ""

        for obj in data_obj:
                                    
            # action = ActionChains(driver)
            # action.move_to_element(obj).perform()
            # 특정 요소가 보일 때까지 스크롤다운 하기 (by the visibility of the element)
            driver.execute_script("arguments[0].scrollIntoView(true);", obj)

            if headless_height != "0":
                driver.execute_script("window.scrollTo(0, window.scrollY - " + headless_height + ");")
                time.sleep(2)

            data += obj.text

        return data


    # 크룔링 결과 전송
    # send_results() 함수 추가 작업 필요
    def send_results(self, result_path, l_cd, m_cd, s_cd, menu_cd, data_id, crawling_type, event_date_text):

        tmp_path = os.path.join(config['crawling']['send_tmp_path'], crawling_type)
        crawling_result_path = config['crawling']['result_path']

        os.makedirs(tmp_path, exist_ok=True)
        os.makedirs(crawling_result_path, exist_ok=True)

        # 결과 저장 날짜 정보
        now_yyyy = datetime.now().strftime('%Y')
        now_mm = datetime.now().strftime('%m')
        now_dd = datetime.now().strftime('%d')

        tmp_copy_path = os.path.join(tmp_path, l_cd, m_cd, s_cd, menu_cd, event_date_text[0:4], event_date_text[4:6], event_date_text[6:8], data_id)

        shutil.copytree(result_path, tmp_copy_path)
        time.sleep(10)

        now_time = datetime.now().strftime("%Y%m%d%H%M%S")

        zip_name = l_cd + "_" + m_cd + "_" + s_cd + "_" + menu_cd + "_" + now_time + ".zip"
        zip_path_ym = os.path.join(crawling_result_path, now_yyyy, now_mm)
        os.makedirs(zip_path_ym, exist_ok=True)
        zip_path = os.path.join(zip_path_ym, zip_name)

        new_zips = zipfile.ZipFile(zip_path, 'w')
        
        for folder, subfolders, files in os.walk(tmp_path):
        
            for file in files:
                new_zips.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), tmp_path), compress_type = zipfile.ZIP_DEFLATED)
        
        new_zips.close()

        time.sleep(10)

        if env == "PRD":
            # sfrp 전송
            remote_path = config['ftp']['crawling_path']
            self.ssh_client(zip_path, os.path.join(remote_path, zip_name))

        # 파일 삭제
        shutil.rmtree(os.path.join(tmp_path, l_cd))


