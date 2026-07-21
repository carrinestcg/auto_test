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

def search_claim_(token,player:str, merchant:str):
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)

    start_time = int(start_of_day.timestamp() * 1000)
    end_time = int(end_of_day.timestamp() * 1000)
    API_URL = "http://sit-admin2.tcg.com/tac/api/relay/get/pv2-promo-ticket-discount-claim-list" 
    params={
        "searchDateMode": "claimDate",
        "startDate": start_time,
        "endDate": end_time,
        "customerName": player,
        "page": 1,
        "size": 1000,
        "pid": 640009
    }
    
    headers = header(token,merchant)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params, cookies=cookies, verify=False)
        response_data = response.json()
        value=response_data.get("value", {})
        list=value.get("list", [])
        for claim in list:
            claimId = claim.get("claimId") 
            status=claim.get("status")
            logging.info(f"找到折抵券紀錄: {claim}")
            return claimId, status
        
    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return None, None
    

def main(username,platform):
    
    try:
        token = get_token(platform)
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)
        return  False, None # FIX: 原本沒有 return，取得 token 失敗仍會繼續執行
    
    claim, status = search_claim_(token,username,platform)
    if claim is not None:
        if status == "AVAILABLE":
            logging.info("折抵券狀態為未使用。")
            return claim, status
        elif status == "CANCELLED":
            logging.info("折抵券狀態為取消")
            return claim, status
        elif status == "EXPIRED":
            logging.info("折抵券已經過期")
            return claim, status
        elif status == "RESERVED":
            logging.info("折抵券狀態為使用中")
            return claim, status
        elif status == "USED":
            logging.info("折抵券狀態為已使用 ")
            return claim, status
        
    
    
     
     
