import pytest
import logging
from Extra_Reward import Backend, Frontend, get_claim_id, main
from deposit_api import batch_approve
import requests


USERNAME = "bnm984"
CUSTOMER_ID=6999548
PROMOTION_ID=4023091
EXTRA_PROMOTION_ID=4535115
TICKET_ID_LIST = [1400029, 1400025, 1400030, 1400026] 
TICKET_QUANTITY = 1
AMOUNT = 100
   
   
CREDENTIAL_BE = {
    "operatorName": "carrine03",
    "password": "Test@1234"
}
CREDENTIAL_FE = {
    "username": USERNAME,
    "password": "123qwe"
}

@pytest.fixture(scope="session")
def extra_claim_id_list():
    backend = Backend(CREDENTIAL_BE)
    frontend = Frontend(CREDENTIAL_FE)
    assert backend.token, "後端登入失敗"
    assert frontend.token, "前端登入失敗"
    
    backend.create_bonus(USERNAME, 5, 0, TICKET_ID_LIST, TICKET_QUANTITY, PROMOTION_ID)
    customer_id, claim_id, promo_type = backend.Search_Customer_bonus(USERNAME)
    backend.Confirm_Customer_bonus([{"promoClaimId": claim_id, "promotionType": promo_type}])

    # 前端領券、充值
    trans_id_list = frontend.get_Ticket_transaction_ID("gi8viet", USERNAME, TICKET_ID_LIST)
    frontend.approve_to_receive_ticket(trans_id_list)
    
    result = get_claim_id(CUSTOMER_ID, EXTRA_PROMOTION_ID)
    logging.info(f"翻倍 claimId list: {result}")
    return result

def test_get_extra_reward_flow(extra_claim_id_list):

    assert extra_claim_id_list is not None, "沒拿到翻倍 claimId"
    assert len(extra_claim_id_list) > 0, "翻倍 claimId list 是空的"
    
    
def test_deposit_to_get_extra_reward(extra_claim_id_list):
    
    frontend = Frontend(CREDENTIAL_FE)
    frontend.deposit_QAD(USERNAME, AMOUNT, EXTRA_PROMOTION_ID)
    batch_approve()
    
    backend=Backend(CREDENTIAL_BE)
    
    API_URL="http://sit-admin2.tcg.com/tac/api/relay/get/promo-promotion-extra-reward-claim-list"
    
    from datetime import datetime
    today = datetime.now()
    start_time = int(datetime(today.year, today.month, today.day, 0, 0, 0).timestamp() * 1000)
    end_time = int(datetime(today.year, today.month, today.day, 23, 59, 59).timestamp() * 1000)
    claimId_list=[]
    
    params={
        "page":1,
        "size":10,
        "sortOrder":"desc",
        "searchDateMode":"createTime",
        "startTime":start_time,
        "endTime":end_time,
        "customerName":USERNAME
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": backend.token,  
        "Connection": "keep-alive",
        "Language": "zh_CN",
        "Merchant": "gi8viet",
        "Referer": "http://sit-admin2.tcg.com/24800",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "customTimezone": "Etc/GMT-8",
        "environment": "TCG3",
        "merchantCode": "gi8viet",
        "platform": "TCG"
    }
    cookies = {"language": "zh_CN"}
    
    response = requests.get(API_URL, params=params, headers=headers, cookies=cookies, verify=False)
    
    assert response.status_code == 200, f"API 回傳非 200，實際：{response.status_code}"
    
    response_json = response.json()
    assert response_json.get("success"), f"API success=False，回應：{response_json}"
    
    value_list = response_json.get("values", [])
    for item in value_list:
        claimId = item.get("claimId")
        claimId_list.append(claimId)
        
    logging.info(f"API 回傳的 claimId list: {claimId_list}")
    logging.info(f"fixture 的 claimId list: {extra_claim_id_list}")
    assert len(value_list) > 0, f"查無 {USERNAME} 的翻倍記錄"
    
    for claim in extra_claim_id_list:
        assert claim in claimId_list, f"claim {claim} 不在 API 回應中"
        
    