"""
手工報名活動回歸測試
涵蓋：前台報名，後台審核

執行方式：
    pytest tests/test_manual_sign.py -v
    pytest tests/test_manual_sign.py::TestManualSign -v
    pytest tests/test_manual_sign.py -v --html=report.html --self-contained-html
"""

import pytest
import requests
from datetime import datetime,timedelta
from MANUAL_SIGN import Backend, Frontend
import logging


BASE_URL_BE = "http://sit-admin2.tcg.com"
BASE_URL_FE = "http://www.sit-gi8viet.com"
PLATFORM = "gi8viet"

TEST_USERNAME = "bnm555"    
PROMOTION_ID=4543098

CREDENTIAL_BE = {
    "operatorName": "carrine03",
    "password": "Test@1234"
}
CREDENTIAL_FE = {
    "username": TEST_USERNAME,
    "password": "123qwe"
}
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@pytest.fixture(scope="session")
def backend():
    b = Backend(CREDENTIAL_BE)
    assert b.token, "後端登入失敗"
    return b


@pytest.fixture(scope="session")
def frontend():
    f = Frontend(CREDENTIAL_FE)
    assert f.token, "前端登入失敗"
    return f

@pytest.fixture(scope="session")
def fe_sign_done(frontend):
    """正向：前台參與報名活動"""
    login_URL="http://www.sit-gi8viet.com/wps/relay/MCSFE_signUpPromotionJoin"

    headers={
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                "Authorization":frontend.token,
                'Connection': 'keep-alive',
                'Language': 'EN',
                'Origin': 'http://www.sit-gi8viet.com',
                'Referer': 'http://www.sit-gi8viet.com/promotions',
                'ModuleId': 'DPSTBAS3',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',  
                
            }
    payload={
                "promotionId": PROMOTION_ID
            }
    
    response = requests.post(login_URL, headers=headers, json=payload, verify=False)
    response_json = response.json()
            
    assert response.status_code == 200, f"API 回傳非 200，實際：{response.status_code}"
    assert response_json.get("success"), f"回傳false {response_json}"    
    return True

@pytest.fixture(scope="session")
def record_ids(backend, fe_sign_done):
    API_URL3="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-signUpList-search-get"
    record_ids = []
    headers=backend.header()
    cookies = {
        "language": "zh_CN"
    }

    params={
        "userName": TEST_USERNAME,
        "promotionName": "",
        "status": "",
        "pageSize": 10,
        "pageNo": 1,
        "merchantCode": "gi8viet",
    }
    
    response=requests.get(API_URL3, cookies=cookies,params=params,headers=headers, verify=False)
    assert response.status_code == 200, f"Request 失敗，status code: {response.status_code}"
    response_data=response.json()
    assert response_data.get("success"), f"沒有拿到record list{response_data}"
    record_id_list=response_data.get("value")
    for value in record_id_list:
        record_id=value.get("recordId")
        assert record_id is not None, f"某筆資料缺少 recordId: {value}"
        logging.info("拿到recordid")
        record_ids.append(record_id)
    return record_ids
        
    
def test_FE_Sign(fe_sign_done):
    
    assert fe_sign_done, "前台報名未完成"
    logging.info("前台報名成功")
    
def test_get_record_list(record_ids):     
    assert len(record_ids) > 0, "record list 不能為空" 
    logging.info(f"共取得 {len(record_ids)} 筆 record")

def test_BE_Approve(backend, record_ids):
   
    for record in record_ids:
        value_dict=backend.get_payload__detail(record)
        assert len(value_dict) > 0, "拿到空字典"
        result=backend.Approve_to_send_bounus(TEST_USERNAME, PROMOTION_ID, record, value_dict)
        assert result.get("success"), f"Approve 失敗，record: {record}，回傳: {result}"
        logging.info(f"record {record} Approve 成功")
     
       
        
        
