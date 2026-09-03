import requests,logging
from datetime import datetime,timedelta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def header(token):
    return{
        
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/20000",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "platform": "TCG"
    
    }
def get_token():
    login_url="http://sit-admin2.tcg.com/tac/api/login/password"
    payload={
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Merchant": "gi8viet",
        "MerchantCode": "gi8viet",
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "",
        "language": "zh_CN",
        "noErrorNotice": "true",
        "platform": ""
    }
    
    cookies = {
        "language": "zh_CN"
    }
    requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
    token_data=requests_data.json()
    return token_data.get("token")


def KYC(token):
    API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/vis-free-spin-v2-createFreeSpinEvent" 
    start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
    payload={
    "vendorCode": "JL",
    "tcgCurrency": "THB",
    "spinLimit": 50,
    "status": 1,
    "startDate": start_time,
    "endDate": end_time,
    "specificVendorParams": {},
    "gameList": [
        {
            "gameId": "35",
            "roomId": "JL0021",
            "betAmount": 3
        }
    ],
    "menuId": 160002
}

    headers = header(token)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        
        
        response_data = response.json()
        
        
        if response_data.get('success') == True:
            logging.info(f"創建kyc方案成功: ")
            
            return True
            
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.info(f"創建kyc方案失败: {error_msg}")
            return False
        
    except Exception as e:
        logging.error(f"狀態碼: {response.status_code}",e)
        return False
def get_event(token,merchantCode):
    try:
        API_URL="http://sit-admin2.tcg.com/tac/api/relay/get/vis-free-spin-v2-getFreeSpinEvent"
        start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        params={
        
        "relayDisableEncode": "true",
        "startDate": start_time,
        "endDate": end_time,
        "status": 1,
        "currentPage" : 1,
        "pageSize" : 10,
        }
        headers = header(token)
        cookies = {
        "language": "zh_CN"
        }
        
        response=requests.get(API_URL, params=params,cookies=cookies,verify=False, headers=headers)
        response_data = response.json()

        if response_data.get('success')==True:
            value = response_data.get('value', [])
            for item in value:
                eventId= item.get('eventId')
                logging.info(f"成功拿到ID: {eventId}")
                return eventId
        else:
            logging.info(f"未成功拿到ID")
            return None
    except Exception as e:
        logging.error(f"拿 ID 時發生錯誤: {e}")
        return None

def create_free_spin_event(token, merchantCode, eventId):
    API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/vis-free-spin-v2-createFreeSpinEventMerchant"
    
    payload = {
    "eventId": str(eventId),
    "merchantList": [
        {
            "merchantCode": merchantCode,
            "freeRounds": 3
        }
    ]
}

    headers = header(token)
    cookies = {
        "language": "zh_CN"
    }
    params={
        "menuId": 160005,
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers, params=params, cookies=cookies, verify=False)
        response.raise_for_status()
        
        response_data = response.json()
        logging.info(response_data)
        if response_data.get('success') == True:
            logging.info(f"創建kyc方案成功: ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.info(f"創建kyc方案失败: {error_msg}")
            return False
        
    except Exception as e:
        logging.error(f"狀態碼: {response.status_code}", e)
        return False
def implement(merchantCode):
    
    deposit_Info = None
    try:
        token=get_token()
        KYC(token)
        eventID=get_event(token,merchantCode)
        result=create_free_spin_event(token, merchantCode, eventID)
        if result:
            logging.info("成功創建kyc方案")
            return True
        else:
            logging.info("創建kyc方案失敗")
            return False
    except Exception as e:
        logging.error(f"執行過程中發生錯誤: {e}")
        return False
        