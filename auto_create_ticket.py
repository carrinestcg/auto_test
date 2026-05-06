import schedule
import time,random
import requests,logging,json
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

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
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Merchant": merchantCode,
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/24786",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "merchantCode": merchantCode,
    "platform": "TCG"
    }
def cookie():
    return {
        "language": "zh_CN"
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

def create_ticket_cash(token,localizations,merchantCode):
    API_URL = "http://10.80.1.20:7001/promo-be/resources/ticket/CASH_VOUCHER" 
    payload = {
    "merchantCode": "gi8viet",
    "type": "CASH_VOUCHER",
    "status": "ISSUING",
    "defaultLanguage": "CN",
    "turnoverMultiplier": 0,
    "dayValidity": 1,
    "hourValidity": 0,
    "claimDevice": None,
    "hasRewardTickets": False,
    "rewardTickets": [],
    "configs": [
        {
            "type": "BONUS",
            "winningPercentage": 100,
            "amount": 1
        }
    ],
    "localizations": localizations,
    "effectType": "IMMEDIATE",
    "rewardTicketValidityType": "TICKET_PROMOTION",
    "rewardStrategy": "FIXED",
    "internalRemark": "c",
    "validityType": "DAY_VALIDITY",
    "validMode": "PERIOD_VALIDITY",
    "productType": "RNG_OR_LIVE",
    "fixedTimeFrom": None,
    "fixedTimeTo": None,
    "claimCondition": {
        "bankCardRequired": False,
        "bankCardTypeRequired": False,
        "requireBankCardType": [],
        "payeeNameRequired": False,
        "addressRequired": False,
        "emailRequired": False,
        "whatsAppRequired": False,
        "lineRequired": False,
        "qqRequired": False,
        "zaloRequired": False,
        "wechatRequired": False,
        "facebookRequired": False,
        "telegramRequired": False,
        "viberRequired": False,
        "appleIdRequired": False,
        "twitterRequired": False,
        "birthdayRequired": False,
        "mobileNumRequired": False,
        "idNoRequired": False,
        "depositRequired": False,
        "turnoverRequired": False,
        "negativeProfitRequired": False,
        "shareContactRequired": False,
        "inviteFriendsRequired": False,
        "depositAmountRequired": False,
        "paymentMethodRequired": False,
        "requirePaymentMethod": [],
        "depositAmountDuration": "AFTER_CLAIM",
        "requireDepositAmount": 0,
        "depositCountRequired": False,
        "depositCountDuration": "AFTER_CLAIM",
        "requireDepositCount": 0,
        "minTurnoverRequired": False,
        "minTurnoverAmt": 0,
        "minTurnoverDuration": "AFTER_CLAIM",
        "gameRequired": False,
        "gameType": "ALL",
        "gameVendor": "ALL",
        "negativeProfitDuration": "AFTER_CLAIM",
        "negativeProfitAmount": 0,
        "inviteFriendsCount": 0,
        "sharedMessage": "欢迎加入 gi8viet越南彩！",
        "shareContactCount": 0
    }
}

    headers =header(token,merchantCode)
    cookies = cookie()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success") :
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def create_ticket_raffle(token,localizations,merchantCode):
    API_URL = "http://10.80.1.20:7001/promo-be/resources/ticket/RAFFLE" 
    payload = {
    "merchantCode": "gi8viet",
    "type": "RAFFLE",
    "status": "ISSUING",
    "defaultLanguage": "CN",
    "turnoverMultiplier": 5,
    "dayValidity": 1,
    "hourValidity": 0,
    "claimDevice": None,
    "hasRewardTickets": False,
    "rewardTickets": [],
    "configs": [
        {
            "type": "BONUS",
            "winningPercentage": 100,
            "minAmount": 50,
            "maxAmount": 100
        }
    ],
    "localizations": localizations,
    "effectType": "IMMEDIATE",
    "rewardTicketValidityType": "TICKET_PROMOTION",
    "validityType": "DAY_VALIDITY",
    "validMode": "PERIOD_VALIDITY",
    "productType": "RNG_OR_LIVE",
    "fixedTimeFrom": None,
    "fixedTimeTo": None,
    "claimCondition": {
        "bankCardRequired": False,
        "bankCardTypeRequired": False,
        "requireBankCardType": [],
        "payeeNameRequired": False,
        "addressRequired": False,
        "emailRequired": False,
        "whatsAppRequired": False,
        "lineRequired": False,
        "qqRequired": False,
        "zaloRequired": False,
        "wechatRequired": False,
        "facebookRequired": False,
        "telegramRequired": False,
        "viberRequired": False,
        "appleIdRequired": False,
        "twitterRequired": False,
        "birthdayRequired": False,
        "mobileNumRequired": False,
        "idNoRequired": False,
        "depositRequired": False,
        "turnoverRequired": False,
        "negativeProfitRequired": False,
        "shareContactRequired": False,
        "inviteFriendsRequired": False,
        "depositAmountRequired": False,
        "paymentMethodRequired": False,
        "requirePaymentMethod": [],
        "depositAmountDuration": "AFTER_CLAIM",
        "requireDepositAmount": 0,
        "depositCountRequired": False,
        "depositCountDuration": "AFTER_CLAIM",
        "requireDepositCount": 0,
        "minTurnoverRequired": False,
        "minTurnoverAmt": 0,
        "minTurnoverDuration": "AFTER_CLAIM",
        "gameRequired": False,
        "gameType": "ALL",
        "gameVendor": "ALL",
        "negativeProfitDuration": "AFTER_CLAIM",
        "negativeProfitAmount": 0,
        "inviteFriendsCount": 0,
        "sharedMessage": "欢迎加入 gi8viet越南彩！",
        "shareContactCount": 0
    }
}

    headers =header(token,merchantCode)
    cookies = cookie()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success") :
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def create_ticket_Egg(token,localizations,merchantCode):
    API_URL = "http://10.80.1.20:7001/promo-be/resources/ticket/GOLDEN_EGG" 
    payload = {
    "merchantCode": "gi8viet",
    "type": "GOLDEN_EGG",
    "status": "ISSUING",
    "defaultLanguage": "CN",
    "turnoverMultiplier": 0,
    "dayValidity": 1,
    "hourValidity": 0,
    "claimDevice": None,
    "hasRewardTickets": False,
    "rewardTickets": [],
    "configs": [
        {
            "winningPercentage": 12.5,
            "type": "BONUS",
            "amount": 5
        },
        {
            "winningPercentage": 12.5,
            "type": "POINT",
            "amount": 5
        },
        {
            "winningPercentage": 12.5,
            "type": "BONUS",
            "amount": 50
        },
        {
            "winningPercentage": 12.5,
            "type": "POINT",
            "amount": 5
        },
        {
            "winningPercentage": 12.5,
            "type": "BONUS",
            "amount": 4
        },
        {
            "winningPercentage": 12.5,
            "type": "POINT",
            "amount": 3
        },
        {
            "winningPercentage": 12.5,
            "type": "BONUS",
            "amount": 2
        },
        {
            "winningPercentage": 12.5,
            "type": "POINT",
            "amount": 1
        }
    ],
    "localizations": localizations,
    "effectType": "IMMEDIATE",
    "rewardTicketValidityType": "TICKET_PROMOTION",
    "productType": "RNG_OR_LIVE",
    "validityType": "DAY_VALIDITY",
    "validMode": "PERIOD_VALIDITY",
    "fixedTimeFrom": None,
    "fixedTimeTo": None,
    "claimCondition": {
        "bankCardRequired": False,
        "bankCardTypeRequired": False,
        "requireBankCardType": [],
        "payeeNameRequired": False,
        "addressRequired": False,
        "emailRequired": False,
        "whatsAppRequired": False,
        "lineRequired": False,
        "qqRequired": False,
        "zaloRequired": False,
        "wechatRequired": False,
        "facebookRequired": False,
        "telegramRequired": False,
        "viberRequired": False,
        "appleIdRequired": False,
        "twitterRequired": False,
        "birthdayRequired": False,
        "mobileNumRequired": False,
        "idNoRequired": False,
        "depositRequired": False,
        "turnoverRequired": False,
        "negativeProfitRequired": False,
        "shareContactRequired": False,
        "inviteFriendsRequired": False,
        "depositAmountRequired": False,
        "paymentMethodRequired": False,
        "requirePaymentMethod": [],
        "depositAmountDuration": "AFTER_CLAIM",
        "requireDepositAmount": 0,
        "depositCountRequired": False,
        "depositCountDuration": "AFTER_CLAIM",
        "requireDepositCount": 0,
        "minTurnoverRequired": False,
        "minTurnoverAmt": 0,
        "minTurnoverDuration": "AFTER_CLAIM",
        "gameRequired": False,
        "gameType": "ALL",
        "gameVendor": "ALL",
        "negativeProfitDuration": "AFTER_CLAIM",
        "negativeProfitAmount": 0,
        "inviteFriendsCount": 0,
        "sharedMessage": "欢迎加入 gi8viet越南彩！",
        "shareContactCount": 0
    }
}

    headers =header(token,merchantCode)
    cookies = cookie()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success") :
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def create_ticket_Wheel(token,localizations,merchantCode):
    API_URL = "http://10.80.1.20:7001/promo-be/resources/ticket/PRIZE_WHEEL"
    payload = {
        "merchantCode": "gi8viet",
        "type": "PRIZE_WHEEL",
        "status": "ISSUING",
        "defaultLanguage": "CN",
        "turnoverMultiplier": 0,
        "dayValidity":1,
        "hourValidity": 0,
        "claimDevice": None,
        "hasRewardTickets": False,
        "rewardTickets": [],
        "configs": [
            {
                "winningPercentage": 12.5,
                "type": "POINT",
                "amount": 6,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            },
            {
                "winningPercentage": 12.5,
                "type": "BONUS",
                "amount": 5,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            },
            {
                "winningPercentage": 12.5,
                "type": "MERCHANDISE",
                "amount": 0,
                "imageUrl": "https://images.21947392.com/sit-images/ticket/gi8viet/2113085_1751966266669.svg",
                "imageName": "2113085_1751966266669.svg",
                "customProductQuantity": 100,
                "productName": {
                    "CN": "test"
                },
                "productDescription": {
                    "CN": "test"
                }
            },
            {
                "winningPercentage": 12.5,
                "type": "BONUS",
                "amount": 4,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            },
            {
                "winningPercentage": 12.5,
                "type": "POINT",
                "amount": 3,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            },
            {
                "winningPercentage": 12.5,
                "type": "BONUS",
                "amount": 2,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            },
            {
                "winningPercentage": 12.5,
                "type": "POINT",
                "amount": 12,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            },
            {
                "winningPercentage": 12.5,
                "type": "POINT",
                "amount": 45,
                "imageUrl": "",
                "imageName": "",
                "customProductQuantity": None
            }
        ],
        "localizations": localizations,
        "effectType": "IMMEDIATE",
        "rewardTicketValidityType": "TICKET_PROMOTION",
        "validityType": "DAY_VALIDITY",
        "validMode": "PERIOD_VALIDITY",
        "productType": "RNG_OR_LIVE",
        "fixedTimeFrom": None,
        "fixedTimeTo": None,
        "claimCondition": {
            "bankCardRequired": False,
            "bankCardTypeRequired": False,
            "requireBankCardType": [],
            "payeeNameRequired": False,
            "addressRequired": False,
            "emailRequired": False,
            "whatsAppRequired": False,
            "lineRequired": False,
            "qqRequired": False,
            "zaloRequired": False,
            "wechatRequired": False,
            "facebookRequired": False,
            "telegramRequired": False,
            "viberRequired": False,
            "appleIdRequired": False,
            "twitterRequired": False,
            "birthdayRequired": False,
            "mobileNumRequired": False,
            "idNoRequired": False,
            "depositRequired": False,
            "turnoverRequired": False,
            "negativeProfitRequired": False,
            "shareContactRequired": False,
            "inviteFriendsRequired": False,
            "depositAmountRequired": False,
            "paymentMethodRequired": False,
            "requirePaymentMethod": [],
            "depositAmountDuration": "AFTER_CLAIM",
            "requireDepositAmount": 0,
            "depositCountRequired": False,
            "depositCountDuration": "AFTER_CLAIM",
            "requireDepositCount": 0,
            "minTurnoverRequired": False,
            "minTurnoverAmt": 0,
            "minTurnoverDuration": "AFTER_CLAIM",
            "gameRequired": False,
            "gameType": "ALL",
            "gameVendor": "ALL",
            "negativeProfitDuration": "AFTER_CLAIM",
            "negativeProfitAmount": 0,
            "inviteFriendsCount": 0,
            "sharedMessage": "欢迎加入 gi8viet越南彩！",
            "shareContactCount": 0
        }
    }


    headers =header(token,merchantCode)
    cookies = cookie()
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success"):
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def create_ticket_Gift(token,localizations,merchantCode):
    API_URL = "http://10.80.1.20:7001/promo-be/resources/ticket/GIFT_CODE"
    payload = {
    "merchantCode": "gi8viet",
    "type": "GIFT_CODE",
    "status": "ISSUING",
    "defaultLanguage": "CN",
    "turnoverMultiplier": 0,
    "dayValidity": 1,
    "hourValidity": 0,
    "claimDevice": None,
    "hasRewardTickets": False,
    "rewardTickets": [],
    "configs": [
        {
            "type": "MERCHANDISE",
            "ticketPrizeId": 63001,
            "winningPercentage": 100
        }
    ],
    "localizations": localizations,
    "effectType": "IMMEDIATE",
    "rewardTicketValidityType": "TICKET_PROMOTION",
    "validityType": "DAY_VALIDITY",
    "validMode": "PERIOD_VALIDITY",
    "fixedTimeFrom": None,
    "fixedTimeTo": None,
    "claimCondition": {
        "bankCardRequired": False,
        "bankCardTypeRequired": False,
        "requireBankCardType": [],
        "payeeNameRequired": False,
        "addressRequired": False,
        "emailRequired": False,
        "whatsAppRequired": False,
        "lineRequired": False,
        "qqRequired": False,
        "zaloRequired": False,
        "wechatRequired": False,
        "facebookRequired": False,
        "telegramRequired": False,
        "viberRequired": False,
        "appleIdRequired": False,
        "twitterRequired": False,
        "birthdayRequired": False,
        "mobileNumRequired": False,
        "idNoRequired": False,
        "depositRequired": False,
        "turnoverRequired": False,
        "negativeProfitRequired": False,
        "shareContactRequired": False,
        "inviteFriendsRequired": False,
        "depositAmountRequired": False,
        "paymentMethodRequired": False,
        "requirePaymentMethod": [],
        "depositAmountDuration": "AFTER_CLAIM",
        "requireDepositAmount": 0,
        "depositCountRequired": False,
        "depositCountDuration": "AFTER_CLAIM",
        "requireDepositCount": 0,
        "minTurnoverRequired": False,
        "minTurnoverAmt": 0,
        "minTurnoverDuration": "AFTER_CLAIM",
        "gameRequired": False,
        "gameType": "ALL",
        "gameVendor": "ALL",
        "negativeProfitDuration": "AFTER_CLAIM",
        "negativeProfitAmount": 0,
        "inviteFriendsCount": 0,
        "sharedMessage": "欢迎加入 gi8viet越南彩！",
        "shareContactCount": 0
    }
}

    headers =header(token,merchantCode)
    cookies = cookie()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success") :
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def create_ticket_Free_spin(token,localizations,merchantCode):
    current_time=datetime.now()
    month_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_time = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)+relativedelta(months=1)-timedelta(milliseconds=1)
    API_URL = "http://10.80.1.20:7001/promo-be/resources/ticket/FREE_SPIN"
    payload = {
    "merchantCode": "gi8viet",
    "status": "ISSUING",
    "defaultLanguage": "CN",
    "localizations": localizations,
    "claimDevice": None,
    "hasRewardTickets": False,
    "internalRemark": "",
    "type": "FREE_SPIN",
    "rewardStrategy": "FIXED",
    "configs": [
        {
            "type": "FREE_GAME",
            "planId": 3624,
            "freeSpinCount": 5,
            "vendorCode": "JL"
        }
    ],
    "validityType": "FIXED_TIME",
    "fixedTimeFrom": 1772726400000,
    "fixedTimeTo": 1777564799000,
    "claimCondition": {
        "bankCardRequired": False,
        "payeeNameRequired": False,
        "addressRequired": False,
        "emailRequired": False,
        "whatsAppRequired": False,
        "lineRequired": False,
        "qqRequired": False,
        "zaloRequired": False,
        "wechatRequired": False,
        "facebookRequired": False,
        "telegramRequired": False,
        "viberRequired": False,
        "appleIdRequired": False,
        "twitterRequired": False,
        "birthdayRequired": False,
        "mobileNumRequired": False,
        "idNoRequired": False,
        "depositRequired": False,
        "turnoverRequired": False,
        "negativeProfitRequired": False,
        "shareContactRequired": False,
        "inviteFriendsRequired": False,
        "sharedMessage": "欢迎加入 gi8viet越南彩！"
    },
    "rewardTicketValidityType": "TICKET_PROMOTION"
}


    headers =header(token,merchantCode)
    cookies = cookie()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success") :
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def get_temu_score(token,merchantCode):
    API_URL = "http://10.80.1.20:7001/promo-be/resources/temu_score"
    headers ={
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Authorization": token,
    "merchantCode":merchantCode,
    "Connection": "keep-alive",
    }
    response=requests.get(API_URL,headers=headers,verify=False)
    response_data=response.json()
    if response_data.get('success'):
        value_list=response_data.get("value",[])
        if value_list:
            temu_score=value_list[0].get("id")
            return temu_score
        else:
            logging.error("沒有拿到list")    
            return None

def create_ticket_temu(token,localizations,temu_score,merchantCode):
    current_time=datetime.now()
    month_start = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_time = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)+relativedelta(months=1)-timedelta(milliseconds=1)
    API_URL = "http://10.80.1.20:7001/promo-be/resources/temu_ticket"
    payload = {
  "defaultLanguage": "CN",
  "localizations": localizations,
  "targetScore": 1,
  "initScoreConfigId": temu_score,
  "claimConditions": [
    {
      "scoreConfigId": temu_score,
      "bankCardRequired": "Y",
      "payeeNameRequired": "Y",
      "addressRequired": "Y",
      "emailRequired": "Y",
      "whatsAppRequired": "Y",
      "lineRequired": "Y",
      "qqRequired": "Y",
      "zaloRequired": "Y",
      "wechatRequired": "Y",
      "facebookRequired": "Y",
      "telegramRequired": "Y",
      "viberRequired": "Y",
      "appleIdRequired": "Y",
      "twitterRequired": "Y",
      "birthdayRequired": "Y",
      "mobileNumBound": "Y",
      "mobileNumRequired": "Y",
      "idNoRequired": "Y",
      "depositRequired": "Y",
      "betRequired": "Y",
      "negativeProfitRequired": "Y",
      "shareContactRequired": "Y",
      "inviteeRequired": "Y",
      "bankCardTypeRequired": True,
      "requireBankCardType": [
        "BANK_ACCOUNT"
      ],
      "paymentMethodRequired": True,
      "requirePaymentMethod": [
        "10"
      ],
      "depositAmountRequired": True,
      "requireDepositAmount": 100,
      "depositCountRequired": True,
      "requireDepositCount": 5,
      "betGameRequired": True,
      "requireBetGameVendor": "CQ9",
      "requireBetGameType": "FISH",
      "betAmountRequired": True,
      "requireBetAmount": 100,
      "requireNegativeProfitAmount": 100,
      "shareContactCount": 1,
      "sharedMessage": "sharedMessage",
      "sharedDescription": "sharedDescription",
      "inviteeCountRequired": True,
      "requireInviteeCount": 10,
      "inviteeRewardCount": 3,
      "cycleInviteeCountRequired": True,
      "requireCycleInviteeCount": 1,
      "cycleInviteeRewardCount": 1,
      "cycleTotalInviteeCountRequired": True,
      "requireCycleTotalInviteeCount": 5,
      "cycleTotalInviteeRewardCount": 1,
      "priority": 1,
      "requireBankCardTypeStr": "string",
      "requirePaymentMethodStr": "string"
    }
  ],
  "ticketValidity": {
    "validityType": "FIXED_TIME",
    "fixedTimeFrom": month_start,
    "fixedTimeTo": end_time,
    "effectType": "IMMEDIATE",
    "dayValidity": 15,
    "hourValidity": 10,
    "timeZone": "GMT+8"
  },
  "claimDevice": None,
  "ticketTurnover": {
    "turnoverType": "MULTIPLIER",
    "turnoverMultiplier": 1.5,
    "turnoverAmount": 100
  },
  "rewardTickets":[],
  "rewardTicketValidityType": None,
  "internalRemark": None
}


    headers =header(token,merchantCode)
    cookies = cookie()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        
        response_data = response.json()
        
        if response_data.get("success"):
            logging.info("創建票卷成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"創建票卷失敗: {error_msg}")
            return False
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return False
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return False
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return False
def main(ticket,localizations,merchantCode):
    token = get_token()
    ticket_dict={
        "CASH":lambda:create_ticket_cash(token,localizations,merchantCode),
        "RAFFLE":lambda:create_ticket_raffle(token,localizations,merchantCode),
        "GOLDEN_EGG":lambda:create_ticket_Egg(token,localizations,merchantCode),
        "WHEEL":lambda:create_ticket_Wheel(token,localizations,merchantCode),
        "GIFT":lambda:create_ticket_Gift(token,localizations,merchantCode),
        "FREE_SPIN":lambda:create_ticket_Free_spin(token,localizations,merchantCode),
        "TEMU":lambda score=None:create_ticket_temu(token,localizations,score,merchantCode)
    }
    if ticket in ticket_dict:
        if ticket=="TEMU":
            score=get_temu_score(token,merchantCode)
            ticket_dict[ticket](score)
        else:
            ticket_dict[ticket]()

'''
if __name__ == "__main__":
    try:
        token = get_token()
        print("取得的 token:", token)
        main()
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)
   '''
    
    
    

   