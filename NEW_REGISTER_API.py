import requests
import logging
from DB_connect import DB_connect

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def get_token():
    try:
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
    
    except Exception as e:
        logging.error(f"拿取token發生異常{e}")

def header(token,MerchantCode):
    return {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Merchant": MerchantCode,
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/20200",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "merchantCode": MerchantCode,
    "platform": "TCG"
    }
def create_agent(token,player:str,platform:str):

    API_URL = "http://sit-admin2.tcg.com/mcs_console/api/agentInfo/createAgent" 
    params={
        "agentName": player,
        "masterAgentType":2,
    }
    
    config_map = {
        "gi8": [
            {"type": "VIETNAM_LOTTO", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "SBO", "rebateValue": 1.5, "rebateSubordinateLimit": 1.5},
            {"type": "FISH", "rebateValue": 1.5, "rebateSubordinateLimit": 1.5},
            {"type": "ELOTTO", "rebateValue": 120, "rebateSubordinateLimit": 120}
        ],
        "huamei": [
            {"type": "PVP", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "LIVE", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "RNG", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "11X5_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "K3_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "LHC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "PK10_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "SSC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "SSC_3-50", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "BBIN", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "IBC", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "FISH", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "ELOTTO", "rebateValue": 1, "rebateSubordinateLimit": 1}
        ],
        "tcgdemov3": [
            {"type": "11X5_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "11X5_1-102", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "K3_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "LF_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "LHC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "PCB_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "PK10_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "SSC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "ELOTTO", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "SEA_LOTT", "rebateValue": 100, "rebateSubordinateLimit": 100}
        ],
        "rollbet": [
            {"type": "PVP", "rebateValue": 900, "rebateSubordinateLimit": 900},
            {"type": "RNG", "rebateValue": 2, "rebateSubordinateLimit": 2},
            {"type": "VIETNAM_LOTTO", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "FISH", "rebateValue": 800, "rebateSubordinateLimit": 800}
        ],
        "lodibet": [
            {"type": "LIVE", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "ELOTTO", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "SEA_LOTT", "rebateValue": 30, "rebateSubordinateLimit": 30}
        ]
    }
    payload = {
    "merchantCode": platform,
    "agentName": player,
    "configs":config_map.get(platform,[])
    }

    headers = header(token,platform)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.post(API_URL, params=params,json=payload, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        
        
        response_data = response.json()
        logging.info(response.text)

        
        if response_data.get("success") :
            logging.info(f"新建代理玩家成功: {player}")
            return platform
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建代理失敗: {error_msg}")
            return None
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
    
def reset_to_123qwe(customerId:int,merchantCode):
    URL="http://10.80.1.22:7001/tcg-uss-ae/password"
    headers={
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept":"application/json"
    }
    if merchantCode == 'tcgdemov3':
        payload={ 
            "customerId": customerId, 
            "needLogInToChangePassword": True, 
            "password": "qwe123" 
    }
    else:
        payload={ 
            "customerId": customerId, 
            "needLogInToChangePassword": True, 
            "password": "123qwe" 
    }
    response=requests.put(URL,headers=headers,json=payload,verify=False)
    response_data=response.json()
    if response_data.get("success"):
        logging.info("修改密碼成功")
        return True
    else:
        return logging.info("修改密碼失敗")

def main(platform,username_list):
        
    try:
        token = get_token()
        print("取得的 token:", token)
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)
    procedure_type=0   
    print(username_list)
    for username in username_list:
        platform=create_agent(token,username,platform)
        customer_id=DB_connect(f"SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='{platform}@{username}'")
        print(customer_id)
        if customer_id:
            if reset_to_123qwe(customer_id,platform):
                procedure_type=1
            else:
                procedure_type=2
        else:
            logging.error("沒有拿到CustomerID")
    if procedure_type == 1:
        return 1, customer_id
    elif procedure_type == 2:
        return 2, customer_id
    else:
        return None ,None

        

   