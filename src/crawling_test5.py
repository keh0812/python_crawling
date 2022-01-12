import json

# from crawling_main import CrawlingMain
from in_next_tab_onclick_compare import CrawlingPagingMain


if __name__ == '__main__':

    # 수집주기 별 데이터 로드
    collection_file = open('./test5.json', 'rt', encoding='UTF8')

    # crawling target JSON object as 
    collection_list = json.load(collection_file)

    # Closing file
    collection_file.close()

    # 데이터 샘플
    # collection_list = [
    #     {
    #         "l_cd": "C002",
    #         "m_cd": "03",
    #         "s_cd": "008",
    #         "menu_cd": "cooperation",
    #         "template_cd": "detail",
    #         "cycle_cd": "1h"
    #     }
    # ]
    
    # main_svc = CrawlingMain()
    paging_svc = CrawlingPagingMain()

    for collection_data in collection_list:

        # 대분류 코드
        l_cd = collection_data["l_cd"]

        # 중분류 코드
        m_cd = collection_data["m_cd"]
        
        # 소분류 코드
        s_cd = collection_data["s_cd"]
        
        # 메뉴 코드
        menu_cd = collection_data["menu_cd"]

        # 템플릿 코드
        # 상세페이지 이동 : detail, 상세페이지 이동 x : none_detail
        template_cd = collection_data["template_cd"]

        # 수집주기 코드
        # 1시간 : 1h, 1일 : 1d, 7일 : 7d
        cycle_cd = collection_data["cycle_cd"]

        # 크롤링 유형 별 크롤러 호출
        # crawling_main(self, type_code, media_code, menu_code, crawling_type, template_code):
        # if cycle_cd == "batch_1" or cycle_cd == "batch_2" or cycle_cd == "batch_3" or cycle_cd == "batch_4" or cycle_cd == "batch_5":
        paging_svc.crawling_main(collection_data)
        # else:
        # main_svc.crawling_main(collection_data)
