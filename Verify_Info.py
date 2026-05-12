import requests,logging,datetime,random
from datetime import datetime
from Customer_id import main
import string

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def header(token):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Language": "zh_CN",
        "Merchant": "gi8viet",
        "MerchantCode": "gi8viet",
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/311792",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "TCG3",
        "merchantCode": "gi8viet",
        "notPending": "true",
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
    logging.info(f"狀態碼{requests_data.status_code}")
    requests_data.raise_for_status()
    token_data=requests_data.json()
    return token_data.get("token")

def input_mobile_number(customerId:int,number:int):
    token=get_token()
    logging.info(f"傳入的手機號:{number}")
    API_URL=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeMobile?customerId={customerId}&merchantCode=gi8viet&countryCode=66&playerMobile={number}&remark=22"
    headers = header(token)
    cookies = {
        "language": "zh_CN"
    }
    
    try:
        response=requests.post(API_URL, cookies=cookies, headers=headers, verify=False)
        response.raise_for_status()

        response_data=response.json()
        if response_data.get("success"):
            logging.info("手機號輸入成功")  
        else:
            logging.error("手機號驗證失敗")
            return False
    
    except Exception as e:
        logging.error(f"手機號驗證請求失敗{e}")
def verify_phone_number(customerId:int):
    token=get_token()
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-verifyMobile?remark=s&remarks=s&customerId={customerId}"
    
    headers = header(token)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response=requests.post(API_URL3, cookies=cookies, headers=headers, verify=False)
        response.raise_for_status()

        response_data=response.json()
        if response_data.get("success") :
            logging.info("手機號驗證成功")  
        else:
            logging.error("手機號驗證失敗")
            return False
    
    except Exception as e:
        logging.error(f"手機號驗證請求失敗{e}")


def input_personal_id(customerId:int, number:int):
        token=get_token()
        logging.info(f"傳入的身分證ID:{number}")
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeIdNumber?customerId={customerId}&merchantCode=gi8viet&remark=33&idNumber={number}"
        
        headers=header(token)
        cookies = {
            "language": "zh_CN"
        }
        try:
            response=requests.post(API_URL3, cookies=cookies, headers=headers, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") :
                response_data.get('value')
                logging.info("身分證ID輸入成功")  
                return True
            else:
                logging.error("身分證ID輸入失敗")
                return False
        
        except Exception as e:
            logging.error("身分證ID輸入請求失敗")
            return False
            
def input_personal_name(customerId:int, new_Name:int):
    token=get_token()
    logging.info(f"傳入的名字:{new_Name}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changePayeeName?customerId={customerId}&merchantCode=gi8viet&newPayeeName={new_Name}&remark=e&updateCard=true"
    headers=header(token)
    cookies = {
            "language": "zh_CN"
        }
    try:
            response=requests.post(API_URL3, cookies=cookies, headers=headers, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") :
                response_data.get('value')
                logging.info("名字輸入成功")  
                return True
            else:
                logging.error("名字輸入失敗")
                return False
        
    except Exception as e:
        logging.error("名字輸入請求失敗")
        return False
    
def verify_info(PLAYER_ACCOUNT, verify_type):
    try:
        token = get_token()
        print("取得的 token:", token)
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)
    if verify_type == 1:
        number=random.randint(10000000,99999999)
        customer_id=main(PLAYER_ACCOUNT)
        if customer_id:
            input_mobile_number(customer_id,number)
            verify_phone_number(customer_id)
            return True

        else:
            logging.error("沒有拿到CustomerID")
            return False
    elif verify_type == 2:
        
        ID_number=random.randint(100000000,999999999)
        customer_id=main(PLAYER_ACCOUNT)
        if customer_id:
            result = input_personal_id(customer_id, ID_number)
            if result:
                return True
            else:
                return False

        else:
            logging.error("沒有拿到CustomerID")
            return False
    elif verify_type == 3:
        
        name = ''.join(random.choices(string.ascii_uppercase, k=8))
        customer_id=main(PLAYER_ACCOUNT)
        if customer_id:
            result = input_personal_name(customer_id, name)
            if result:
                return True
            else:
                return False

        else:
            logging.error("沒有拿到CustomerID")
            return False
    

    
    

   