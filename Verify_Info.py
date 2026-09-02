from wsgiref import headers

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

def gen_number(a, b):
    return lambda: random.randint(a, b)

def gen_string(k=8):
    return lambda: ''.join(random.choices(string.ascii_uppercase, k=k))

def input_mobile_number(customerId:int,number:int,platform:str):
    token=get_token()
    logging.info(f"傳入的手機號:{number}")
    API_URL=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeMobile?customerId={customerId}&merchantCode={platform}&countryCode=66&playerMobile={number}&remark=22"
    headers = header(token)
    cookies = {
        "language": "zh_CN"
    }
    
    try:
        response=requests.post(API_URL, cookies=cookies, headers=headers, verify=False)
        response.raise_for_status()

        response_data=response.json()
        print(response_data)
        if response_data.get("success"):
            logging.info("手機號輸入成功")  
            return True
        else:
            logging.error("手機號輸入失敗")
            return False
    
    except Exception as e:
        logging.error(f"手機號輸入請求失敗{e}")
        return False
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
            return True
        else:
            logging.error("手機號驗證失敗")
            return False
    
    except Exception as e:
        logging.error(f"手機號驗證請求失敗{e}")
        return False

def _verify_mobile_number(customerId:int, platform:str):
    mobile_number=random.randint(100000000,999999999)
        
    if not input_mobile_number(customerId, mobile_number, platform):
        return False, None
    
    if not verify_phone_number(customerId):
        return False, None
    
    return True, mobile_number
        
def input_personal_id(customerId:int, number:int, platform:str):
        token=get_token()
        logging.info(f"傳入的身分證ID:{number}")
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeIdNumber?customerId={customerId}&merchantCode={platform}&remark=33&idNumber={number}"
        
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
        
def input_personal_picture(customerId:int, number:int):
        token=get_token()
        API_URL3="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeIdPicture"
        
        headers=header(token)
        cookies = {
            "language": "zh_CN"
        }
        payload={
            "remark": "d",
            "message": "d",
            "customerId": customerId,
            "idCardBack":"data:image/jpeg;base64,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",
            "idCardFront":  "data:image/jpeg;base64,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",
            "idCardSelfie": "",
            "extraImage1": "",
            "extraImage2": "",
            "extraImage3": ""
        }     
        
        try:
            response=requests.post(API_URL3, cookies=cookies, headers=headers, json=payload, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") :
                response_data.get('value')
                logging.info("身分證照片上傳成功")  
                return True
            else:
                logging.error("身分證照片上傳失敗")
                return False
        
        except Exception as e:
            logging.error("身分證照片上傳請求失敗")
            return False
        
def confirm_personal_id(customerId:int):
        token=get_token()
        API_URL3="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-verifyIdPicture"
        params={
            "customerId": customerId,
            "remark": "d",
            "message":"d",
            "idVerificationStatus": "Y"
        }
        headers=header(token)
        cookies = {
            "language": "zh_CN"
        }
        try:
            response=requests.post(API_URL3, cookies=cookies, headers=headers, params=params, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") :
                response_data.get('value')
                logging.info("審核成功")  
                return True
            else:
                logging.error("審核失敗")
                return False
        
        except Exception as e:
            logging.error("審核請求失敗")
            return False

def _verify_id_card(customerId:int, platform:str):
    ID_number = random.randint(100000000, 999999999)
        
    if not input_personal_id(customerId, ID_number, platform):
        return False, None
    
    if not input_personal_picture(customerId, ID_number):
        return False, None
    
    if not confirm_personal_id(customerId):
        return False, None
    
    return True, ID_number    
def input_personal_name(customerId:int, new_Name:str, platform:str):
    token=get_token()
    logging.info(f"傳入的名字:{new_Name}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changePayeeName?customerId={customerId}&merchantCode={platform}&newPayeeName={new_Name}&remark=e&updateCard=true"
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
        logging.error(f"名字輸入請求失敗{e}")
        return False
    
def input_wechat_ID(customerId:int, wechat_id:str, platform):
    token=get_token()
    logging.info(f"傳入的WeChat ID:{wechat_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeWechat?customerId={customerId}&merchantCode={platform}&remark=ff&wechat={wechat_id}"
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
                logging.info("WeChat ID輸入成功")  
                return True
            else:
                logging.error("WeChat ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"WeChat ID輸入請求失敗{e}")
        return False
    
def input_address(customerId:int, address:str, platform:str):
    token=get_token()
    logging.info(f"傳入的地址:{address}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeAddress?customerId={customerId}&merchantCode={platform}&remark=ss&address={address}"
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
                logging.info("地址輸入成功")  
                return True
            else:
                logging.error("地址輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"地址輸入請求失敗{e}")
        return False
    
def input_line_ID(customerId:int, line_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Line ID:{line_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeLineId?customerId={customerId}&merchantCode={platform}&remark=d&lineId={line_id}"
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
                logging.info("Line ID輸入成功")  
                return True
            else:
                logging.error("Line ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Line ID輸入請求失敗{e}")
        return False
    
def input_apple_ID(customerId:int, apple_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Apple ID:{apple_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-changeAppleId?customerId={customerId}&merchantCode={platform}&remark=d&appleId={apple_id}"
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
                logging.info("Apple ID輸入成功")  
                return True
            else:
                logging.error("Apple ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Apple ID輸入請求失敗{e}")
        return False

def input_telegram_ID(customerId:int, telegram_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Telegram ID:{telegram_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeTelegram?customerId={customerId}&merchantCode={platform}&remark=x&telegram={telegram_id}"
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
                logging.info("Telegram ID輸入成功")  
                return True
            else:
                logging.error("Telegram ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Telegram ID輸入請求失敗{e}")
        return False
        
def input_twitter_ID(customerId:int, twitter_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Twitter ID:{twitter_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-changeTwitter?customerId={customerId}&merchantCode={platform}&remark=s&twitter={twitter_id}"
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
                logging.info("Twitter ID輸入成功")  
                return True
            else:
                logging.error("Twitter ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Twitter ID輸入請求失敗{e}")
        return False
    
def input_viber_ID(customerId:int, viber_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Viber ID:{viber_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-changeViber?customerId={customerId}&merchantCode={platform}&remark=d&viber={viber_id}"
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
                logging.info("Viber ID輸入成功")  
                return True
            else:
                logging.error("Viber ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Viber ID輸入請求失敗{e}")
        return False

def binding_virtual_wallet(customerId:int, cardNumber:str, platform:str):
    token=get_token()
    logging.info(f"傳入的虛擬錢包 ID:{cardNumber}")
    name=gen_string()()
    API_URL3="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-createBankCard-EW"
    headers=header(token)
    cookies = {
            "language": "zh_CN"
        }
    payload={
            "bankCode": "10659",
            "legalName": name,
            "phone": "343435454354",
            "customerId": customerId,
            "bankName": "EWBANK_CN",
            "merchantCode": "gi8viet",
            "cardNumber": cardNumber,
            "customFields": [],
            "type": "EW"
        }
    try:
            response=requests.post(API_URL3, cookies=cookies, json=payload,headers=headers, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") :
                response_data.get('value')
                logging.info("虛擬錢包綁定成功")  
                return True
            else:
                logging.error("虛擬錢包綁定失敗")
                return False
        
    except Exception as e:
        logging.error(f"虛擬錢包綁定請求失敗{e}")
        return False

def input_whatsapp_ID(customerId:int, whatsapp_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的WhatsApp ID:{whatsapp_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeWhatsAppId?customerId={customerId}&merchantCode={platform}&remark=d&whatsAppId={whatsapp_id}"
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
                logging.info("WhatsApp ID輸入成功")  
                return True
            else:
                logging.error("WhatsApp ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"WhatsApp ID輸入請求失敗{e}")
        return False
    
def input_Facebook_ID(customerId:int, facebook_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Facebook ID:{facebook_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeFacebookId?customerId={customerId}&merchantCode={platform}&remark=d&facebookId={facebook_id}"
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
                logging.info("Facebook ID輸入成功")  
                return True
            else:
                logging.error("Facebook ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Facebook ID輸入請求失敗{e}")
        return False
    
def input_upline(customerId:int, platform:str, newUpline:str):
    token=get_token()
    logging.info(f"傳入的newUpline:{newUpline}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-basic-information-changeUpline"
    header={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": platform,
            "MerchantCode": platform,
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/311792",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "notPending": "true",
            "platform": "TCG"
        }
    params={
        "customerId": customerId,
        "newUpline": newUpline,
        "remark":"d",
        "cascadeType":"D",
        "cancelContractFlag":"Y",
        "dataTransferDate":"2026-08-01"
    }
    cookies = {
            "language": "zh_CN"
        }
    try:
            response=requests.post(API_URL3, cookies=cookies, headers=header, params=params, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") :
                response_data.get('value')
                logging.info("上級代理輸入成功")  
                return True
            else:
                logging.error("上級代理輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"上級代理輸入請求失敗{e}")
        return False
    
def input_zalo_ID(customerId:int, zalo_id:str, platform:str):
    token=get_token()
    logging.info(f"傳入的Zalo ID:{zalo_id}")
    API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-player-security-information-changeZalo?customerId={customerId}&merchantCode={platform}&remark=d&zalo={zalo_id}"
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
                logging.info("Zalo ID輸入成功")  
                return True
            else:
                logging.error("Zalo ID輸入失敗")
                return False
        
    except Exception as e:
        logging.error(f"Zalo ID輸入請求失敗{e}")
        return False
verify_handler={ 
    3: (gen_string(), input_personal_name),
    4: (gen_string(9), input_wechat_ID),
    5: (gen_string(9), input_line_ID),
    6: (gen_string(9), input_apple_ID),
    7: (gen_string(), input_address),
    8: (gen_string(), input_twitter_ID),
    9: (gen_string(), input_viber_ID),
    10: (gen_string(), input_telegram_ID),
    11: (gen_number(1000000000000, 2000000000000), binding_virtual_wallet),
    12: (gen_string(10), input_whatsapp_ID),
    13: (gen_string(9), input_Facebook_ID),
    15: (gen_string(9), input_zalo_ID),
}

def verify_info(PLAYER_ACCOUNT, platform ,verify_type, newUpline):
        
    customer_id=main(PLAYER_ACCOUNT, platform, 1)
    platform=platform[0]
    print(platform)
    if not customer_id:
        logging.error(f"找不到玩家 {PLAYER_ACCOUNT} 的 customer_id")
        return False, None
    
    if verify_type == 1:
        return _verify_mobile_number(customer_id, platform)
        
    elif verify_type == 2:
        return _verify_id_card(customer_id, platform)

    elif verify_type == 14:
        if not (newUpline or "").strip():
            logging.error("上級代理 newUpline 不可為空")
            return False, None
        new_upline = newUpline.strip()
        if input_upline(customer_id, platform, new_upline):
            logging.info(f"驗證類型 14 成功，值: {new_upline}")
            return True, new_upline
        return False, None
        
    gen_value, handler = verify_handler.get(verify_type, (None, None))
    if handler is None:
        logging.error(f"未知的驗證類型: {verify_type}")
        return False, None
    
    value = gen_value() 
    
    if handler(customer_id, value, platform):
        
        logging.info(f"驗證類型 {verify_type} 成功，值: {value}")
        return True, value
    
    return False, None