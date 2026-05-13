import yaml
import os
import requests
import logging
import json
from datetime import datetime,timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def header(token,merchant):
    return {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/24785",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "Merchant": merchant,
    "merchantCode": merchant,
    "platform": "TCG"
    }
def get_token(merchant):
    login_url="http://sit-admin2.tcg.com/tac/api/login/password"
    payload={
        "operatorName": "parisv01",
        "password": "Aa123456@"
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Merchant": merchant,
        "MerchantCode": merchant,
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
    requests_data.raise_for_status()
    token_data=requests_data.json()
    return token_data.get("token")

def create_bonus(token,player:str,bonusAmount:int,bonusPointAmount:int,ticketId:int,amount:int,prmotion_id:int,merchant:str):
    API_URL = "http://10.80.1.19:8083/promo-be/resources/promotion/manual_reward/claims" 
    payload = {
    "promotionId": prmotion_id,
    "customerName": player,
    "internalRemark": "internal remark",
    "playerRemark": "player remark",
    "bonusAmount": bonusAmount,
    "pointAmount": bonusPointAmount,
    "turnoverAmount": 2000,
    "ticketId": ticketId,
    "ticketQuantity": amount,
    "isSendApp": "N",
    
}

    headers = header(token,merchant)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        
        
        response_data = response.json()
        
        
        if response_data.get("success") :
            logging.info("手動紅利發放成功 ")
            return True
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"手動紅利發放失敗: {error_msg}")
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
def Search_Customer_bonus(token,player:str,merchant:str):
    API_URL = "http://sit-admin2.tcg.com/tac/api/relay/get/prom-promotion-manual-reward-claims" 
    start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
    end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
    params = {
    "merchantCode": merchant,
    "status": "P",
    "customerName":player,
    "relayDisableEncode": True,
    "isForProcessingAll": False,
    "periodType": "ISSUE_PERIOD",
    "startTime": start_time,
    "endTime": end_time,
    "pageSize": 10,
    "pageNo": 1,
    "pid" :20250
    }

    headers = header(token,merchant)
    cookie={
        "Cookie": "language=zh_CN"
    }
    try:
        response = requests.get(API_URL, params=params, headers=headers, cookies=cookie, verify=False)
        response.raise_for_status()
        
        response_data = response.json()
        
        if response_data.get("success"):
            logging.info(f"完整回應: {json.dumps(response_data, ensure_ascii=False)}")
            
            customer_list=response_data.get("value",[])
            value = response_data.get("value", {})
            customer_list = value.get("list", [])
            if customer_list:
                customer_info=customer_list[0]
                CustomerID=customer_info.get("customerId")
                claimid=customer_info.get("claimId")
                promoType=customer_info.get("promotionType")
    
                if CustomerID and claimid:
                    logging.info(f"拿到 CustomerID: {CustomerID} 和 claimid: {claimid} {promoType}")
                    return CustomerID, claimid,promoType
        else:
            logging.error(response_data)
            logging.error("回應中找不到 customerId 或 claimid")
            return None, None, None
        
            
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return None, None, None
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return None, None, None
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return None, None, None
  
def Confirm_Customer_bonus(token,Customerid:int,claimid:int,merchant:str ,promoType:str):
    API_URL = f"http://10.80.1.19:8083/promo-be/resources/promotion/manual_reward/claims/{claimid}/approve" 
    payload = {
        "promotionId": 4407096,
        "customerId": Customerid,
        "internalRemark": "string"
    
}

    headers = header(token,merchant)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        
        response_data = response.json()
        
        if response_data.get("success") :
            logging.info("審核活動紅利成功 ")
            return True
        else:
            error_msg = response_data.get("value" )
            logging.error(f"未審核成功 value: {error_msg}{response_data}")
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
def main(username,promotionid,ticket_id,platform,amount):
    
    try:
        token = get_token(platform)
        print("取得的 token:", token)
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)
    
    bonusAmount=1000
    bonusPointAmount=20
    
    create_bonus(token,username,bonusAmount=bonusAmount,bonusPointAmount=bonusPointAmount,ticketId=ticket_id,amount=amount,prmotion_id=promotionid,merchant=platform)
        
    Customerid,claimid,promoType = Search_Customer_bonus(token,username,platform)
    if Customerid is not None and claimid is not None:
        Confirm_Customer_bonus(token,Customerid,claimid,platform,promoType)
    else:
        logging.error("沒有拿到ID")



  