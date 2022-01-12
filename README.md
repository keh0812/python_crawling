# python_crawling

Python Selenium 웹 크롤러(+ 페이징) 코드


## 개발환경
- python 3.7.6


## 패키지 설치
```
pip install pipenv (pipenv 설치가 되어있으면 건너뜀)
set PIPENV_VENV_IN_PROJECT=1 (현재 프로젝트 내부에 가상환경을 설치하는 환경변수)
pipenv --three (환경변수가 잡혀 있는 python3로 가상환경 공간 구성)
pipenv install (Pipfile에 적혀있는 파이썬 모듈을 생성)
```


## 웹드라이버 다운로드
- https://sites.google.com/a/chromium.org/chromedriver/downloads
- 환경에 맞는 드라이버 다운로드

```
- windows
- C:\project\t3q.cep\crawler\chromedriver 경로에 압축 해제
```


## 테스트
- 테스트 데이터 : test.json(1건)
```
cd src-paging
python crawling_test.py
```


## 수집대상 코드 데이터
```
[{
   "l_cd": "C002",
   "m_cd": "03",
   "s_cd": "008",
   "menu_cd": "cooperation",
   "template_cd": "detail",
   "cycle_cd": "1h"
}]
```
- l_cd : 출처 대분류 코드
- m_cd : 출처 중분류 코드
- s_cd : 출처 소분류 코드
- menu_cd : 메뉴 코드
- template_cd : 템플릿 코드
- cycle_cd : 수집 주기

### 1. template_code
- new : 새탭 타입
- modal : 모달 타입
- none : 상세페이지 없는 타입
- detail : 상세페이지 기본 타입
- window_open : 상세페이지 새탭 열기 타입

### 2. cycle_code
- 1h : 1시간
- 1d : 1일
- 7d : 7일


## 수집 대상 공통 데이터 설명
```
 "common_data": {
    "l_cd" : "C002",
    "l_cd_name" : "국내",
    "m_cd": "03",
    "m_cd_name": "연구기관",
    "s_cd": "008",
    "s_cd_name": "통일연구원",
    "menu_cd": "cooperation",
    "menu_name": "KINU연구 - 주제별 - 남북관계 - 교류협력",
    "url": "https://www.kinu.or.kr/www/jsp/prg/api/dlL.jsp",
    "detail_tag": ".txtL a",
    "identifier": "biblioId"
  }
```
- l_cd : 출처 대분류 코드
- l_cd_name : 출처 대분류 코드명
- m_cd : 출처 중분류 코드
- m_cd_name : 출처 중분류 코드
- s_cd : 출처 소분류 코드
- s_cd_name : 출처 소분류 코드명
- menu_cd : 메뉴 코드
- menu_name : 메뉴 명
- url : 수집 대상 URL
- detail_tag : 상세페이지 링크 요소,
- identifier : 게시글 아이디

## 수집 대상 메타 데이터 설명
```
"meta_data": {
   "title_tag": "#cmsContent p",
   "author_tag": "tr:nth-child(1) td",
   "download_tag": "tr:nth-child(5) td a",
   "write_date_tag": "",
   "contents_tag": "#tab_con div",
   "img_tag": ""
}
```
- title_tag : 게시글 제목 요소
- author_tag : 게시글 등록자 요소
- download_tag : 다운로드 일크 요소
- write_date_tag : 게시글 등록일 요소
- contents_tag : 게시글 본문 요소
- img_tag : 게시글 본문 이미지 요소

## 수집 대상 이벤트 데이터 설명
```
"event_data": {
    "identifier": "",
    "menu": ["#main_search1", "#main_search2"],
    "search": {
        "search_input" : "#searchForm #searchKeyWord",
        "search_keyword" : "북한",
        "search_btn" : "#searchForm .btn"
    },
    "tab" : {
        "tab_tag" : "#tab li"
    },
    "modal" :{
        "close_tag": ".modal-footer button"
    },
    "headless" : "#header",
    "url_filtering" : "amp;",
   "login": {
        "url":"http://hri.co.kr/member/memberLogin.asp",
        "id":"t3qadmin",
      "id_input":"#memId",
        "pw":"t3q9327",
        "pw_input":"#memPassword",
        "event_next":"",
        "event_signin":".arr_right input",
        "event":"signin"
    }
}
```
### 1. identifier : 게시글 아이디 생성 이벤트
- slash_after1 : '/' 기준으로 맨 뒤의 값을 게시글 아이디로 리턴
- slash_after2 : '/' 기준으로 맨 뒤에서 2번째 값을 게시글 아이디로 리턴
- slash_after3 : '/' 기준으로 맨 뒤에서 3번째 값을 게시글 아이디로 리턴
- remove_html : '/' 기준으로 맨 뒤의 값에서 'html'문자를 제거한 값을 게시글 아이디로 리턴
- ttmmdd : '/' 기준으로 맨 뒤에서 1번째, 2번째, 3번째, 4번째 값을 게시글 아이디로 리턴
- reverse_40 : 식별자(data_id)를 뒤에서 부터 40자리까지 게시글 아이디로 리턴
- kyungnam : 식별자(data_id)에서 35자리에서 55자리까지 게시글 아이디로 리턴
- url_pass : URL를 게시글 아이디로 리턴
- state : '/'  기준으로 맨 뒤에서 2번째 값의 역순으로 15자리와 '/' 기준으로 맨 뒤에서 3번째 값의 5자리까지를 합쳐서 게시글 아이디로 리턴
### 2. menu : 메뉴 이동 이벤트
- 메뉴 이동에 필요한 요소를 리스트 형태로 관리
- 리스트 순서대로 요소 클릭 이벤트 발생
### 3. search : 키워드 검색 이벤트
- search_input : 키워드 검색 입력창 요소
- search_keyword : 키워드
- search_btn : 검색 이벤트 요소
### 4. tab : 본문 탭 이동 이벤트
- tab_tag : 본문 내 탭 요소
### 5. modal : 모달 제어 이벤트
- close_tag : 모달 닫기 요소
### 6. headless : 해더 영역 높이 제어
- 브라우저에서 화면을 가리는 영역의 요소
### 7. url_filtering : URL 문자 필터링
- URL에 포함되어있는 문자 필터링 처리
### 8. login : 로그인 제어 이벤트
- url : 수집 대상 로그인 화면 URL
- id : 로그인 아이디
- id_input : 로그인 ID 입력창 요소
- pw : 로그인 비밀번호
- pw_input : 로그인 PW 입력창 요소
- event_next : ID 입력 후 다음 버튼 이벤트 요소
- event_signin : 로그인 이벤트 요소
- event : signin 또는 next_signin
    - signin : 아이디 입력 후 다음버튼 없는 요소
   - next_signin : 아이디 입력 후 다음버튼 있는 요소


## 수집 대상 공통 페이징 데이터 설명
```
"paging_data" : {
    "paging_tag": ".hidden-xs .apager a",
    "next_tag": ".number-pager .hidden-xs .fa-chevron-right"
}
```
- paging_tag : 페이지 아이템 요소
- next_tag : 다음 버튼 요소


## 수집 대상 추가 페이징 데이터 설명
```
"paging_data" : {
    "paging_bar" : ".js-pager__items",
    "active_page_tag" : ""
}
```
- paging_bar : 다음 버튼 위치 지정 시 사용       (적용 페이징 파일 : **pagingbar_nopage.py**)
- active_page_tag : 현재 페이지 요소            (적용 페이징 파일 : **no_next_marines.py, activepage_nonext.py**)


## 페이징 파일 리스트


- 30 ~ 42는 북한 데이터 페이징 파일입니다.

| 번호 | 파일명 | 파일 설명 |
| ------ | ------ | ------ |
|1| next_disappear.py | next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 사라짐 / **Arms Control Association, 국방부**에 적용 |
|2| in_next_disappear_nopage_cato.py | **CATO Institute**에 적용 |
|3| next_possible_crs.py | **Congressional Research Service**에 적용 |
|4| pagingbar_nopage.py | paging_tag가 없는 유형, paging_data에 paging_bar 추가 / **WFP, 미국 국방정보국, 미국 법무부, 미국 재무부, 미국 테러금융정보실, 자유아시아방송(RFA), 주한 미국대사관**에 적용  |
|5| in_next_possible_wilson.py | **Wilson Center**에 적용 |
|6| no_next.py | next_tag가 없거나 next_tag 클릭 시 한 탭씩 이동하는 유형 / **경남대학교 극동문제연구소, 국방부**에 적용 |
|7| next_disappear_inss.py | **국가안보전략연구원**에 적용 |
|8| next_tab_href.py | **국가인권위원회, 국방대학교 안보문제연구소, 국토교통부, 농촌진흥청, 북한자료센터, 산업통상자원부, 한국수출입은행**에 적용  |
|9| in_next_tab_onclick_compare.py  | **과학기술정책연구원, 남북회담본부 홈페이지, 통일연구원, 한국개발연구원(KDI**)에 적용 |
|10| in_next_tab_href_compare.py | **기상청**에 적용 |
|11| in_next_tab_onclick_compare_active.py | **국토연구원, 기획재정부, 한국국방연구원**에 적용 |
|12| next_possible_kiep.py | **대외경제정책연구원(KIEP**)에 적용 |
|13| next_disappear_redcross.py | **대한적십자사**에 적용 |
|14| next_tab_href_parse.py | **동아시아연구원(EAI), 무역투자진흥공사(KOTRA**)에 적용 |
|15| next_possible_state.py | **미국 국무부, 미국 정보조사국**에 적용 |
|16| next_impossible_defense.py | **미국 국방부**에 적용 |
|17| paging_url_white.py | **미국 백악관**에 적용 |
|18| no_next_marines.py | **미국 해병정보국**에 적용 |
|19| in_next_tab_unicode_puac.py | **민주평화통일자문회의**에 적용 |
|20| next_tab_onclick_moj.py | **법무부**에 적용 |
|21| next_tab_mofa.py | **주독한국대사관, 주러한국대사관, 주미한국대사관, 주심양 총영사관, 주일한국대사관, 주중한국대사관**에 적용 |
|22| next_tab_nkinfo.py | **북한정보포털**에 적용 |
|23| next_tab_href_compare.py | **한국무역협회**에 적용 |
|24| in_next_tab_href_parse_active.py | **한국농촌경제연구원**에 적용 |
|25| next_tab_onclick.py | **청와대, 한국문화관광연구원**에 적용 |
|26| activepage_nonext.py | **통일교육원 홈페이지, 한미경제연구소(KEI**)에 적용 |
|27| in_next_tab_href_compare_active.py | **한국은행**에 적용 |
|28| next_tab_href_parse_active.py | **외교부, 외교안보연구소**에 적용 |
|29| next_impossible_me.py | **환경부**에 적용 |
|30| no_next_naenara.py | **내나라**에 적용 |
|31| in_next_tab_href_parse_ryomyung.py | **려명**에 적용 |
|32| in_next_tab_href_compare_ryugyong.py | **류경**에 적용 |
|33| no_next_minzu.py | **민주조선**에 적용 |
|34| pagingbar_nonext.py | **우리민족강당**에 적용 |
|35| in_next_tab_href_uri.py | **우리민족끼리**에 적용 |
|36| in_next_tab_href_parse_tourismdprk.py | **조선관광**에 적용 |
|37| next_tab_href_tourkgs.py | **조선금강산국제여행사**에 적용 |
|38| next_tab_href_dprktoday.py | **조선의 오늘**에 적용 |
|39| in_next_tab_href_parse.py | **청년전위**에 적용 |
|40| in_next_tab_href_parse_uriminzokkiri.py | **통일신보**에 적용 |
|41| in_next_tab_href_compare.py | **메아리, 통일의 메아리**에 적용 |
|42| pyungyangtimes.py | **평양타임즈**에 적용 |



## 페이징 유형 코드


| 번호 | 유형명 | 유형 설명 |
| ------ | ------ | ------ |
|1| next_disappear | next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 사라짐 |
|2| in_next_disappear | next, last, prev.. 가 .paging에 모두 포함된 경우, next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 사라짐 |
|3| no_next | next(>) 버튼 없음 |3|
|4| next_possible | next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 클릭 가능 |
|5| in_next_possible | next, last, prev.. 가 .paging에 모두 포함된 경우, next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 클릭 가능 |
|6| next_tab | next(>) 클릭 시 한 탭 씩 증가 |
|7| in_next_tab | next, last, prev.. 가 .paging에 모두 포함된 경우, next(>) 클릭 시 한 탭 씩 증가 |
|8| next_impossible | next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 클릭 불가 |
|9| in_next_impossible | next, last, prev.. 가 .paging에 모두 포함된 경우, next(>) 클릭 시 1페이지 씩 증가 , 마지막에 next 클릭 가능 |
|10| 개별 유형 |  |
|-| 총 개수 |  |





