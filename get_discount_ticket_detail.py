import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def header(token,merchantCode):
    return{
        
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Merchant": merchantCode,
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/20000",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "merchantCode": merchantCode,
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


def get_ticket_detail(ticket_id):
    URL = "http://10.81.1.88:8083/promo-be/resources/ticket/discount"
    headers = header(get_token(),"gi8viet")
    response = requests.get(URL, headers=headers, verify=False)
    response_json = response.json()
    if response.status_code == 200:
        value = response_json.get("value", {})
        id = value.get("id")
        if id == ticket_id:
            logging.info(f"Found ticket with ID {ticket_id}")
            requiredDepositAmount = value.get("configs")[0].get("requiredDepositAmount") 
            return requiredDepositAmount

        else:
            logging.warning(f"Ticket with ID {ticket_id} not found in the response.")
            return None
    else:
        logging.error(f"Failed to get ticket detail. Status code: {response.status_code}, Response: {response_json}")
        return []
    