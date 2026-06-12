import requests
import logging
import random
import aiohttp
import asyncio
import json
import time
from datetime import timedelta
from DB_connect import DB_connect
from Customer_id import main


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
URL="http://10.81.1.22:7001/tcg-uss-ae/customer-create/register"
login_url='http://www.sit-gi8viet.com/wps/session/login/unsecure'




async def get_token_login(session, username, password):
        
            
        login_url='http://www.sit-gi8viet.com/wps/session/login/unsecure'
            
        headers = {
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                
            }
        login_data={
                'username':username,
                'password':password
            } 
        try:
            async with session.post(login_url,json=login_data,headers=headers,ssl=False) as resp:
                request_data=await resp.json()
                if request_data.get("value"):
                    username = request_data['value']['userName']
                    userid = request_data['value']['id']
                    token=request_data['value']['token']

                    return token
                else:
                    logging.error(f"{username} 登入失敗: {request_data}")
                    return None
        
        except aiohttp.ClientError as e:
            logging.error(f"請求失敗{e}")
            return None

async def Create_member(session,CustomerName,MerchantCode):
    start=time.time()
    mobile_num=random.randint(1000000000,9999999999)
    uuid=random.randint(100000000,999999999)
    header={
        "Language":"CN",
        "Content-Type":"application/json"
    }
    payload={ 
            "activeFlag":0,
            "customerName":f"{MerchantCode}@{CustomerName}", 
            "email":f"{CustomerName}@{MerchantCode}.com", 
            "hashAlgorithm":0, 
            "loginLanguage":"CN", 
            "merchantCode":MerchantCode, 
            "password":"123qwe", 
            "glifeId":f"{CustomerName}", 
            "mayaId":f"{CustomerName}", 
            "profile":{ 
            "address":"Osaka", 
            "city":"Osaka", 
            "countryCode":"Taipei", 
            "createSuboFlag":0, 
            "gender":0, 
            "idType":0, 
            "mobileNo":f"{mobile_num}", 
            "sourceOfIncome":0, 
            "type":0, 
            "zipcode":"111", 
            "idVerification":1, 
            "idVerificationStatus":"Y", 
            "appleId":f"{CustomerName}", 
            "facebookId":f"{CustomerName}", 
            "lineId":f"{CustomerName}", 
            "lineUuid":f"U80b36f48e3bc89b7{uuid}d00429d", 
            "qqNo":f"{CustomerName}", 
            "telegram":f"{CustomerName}", 
            "viber":f"{CustomerName}", 
            "twitter":f"{CustomerName}", 
            "twitterId":f"{CustomerName}", 
            "wechat":f"{CustomerName}", 
            "whatsAppId":f"{CustomerName}", 
            "zalo":f"{CustomerName}", 
            "recommenderId":2151008, 
            "level_id":2151008 
            } 
            }
    
    try:
        async with session.post(URL,headers=header,json=payload,ssl=False)as resp:
            text=await resp.text()
            end=time.time()
            try:
                data=json.loads(text)
            except Exception as e:
                logging.info(f"[{CustomerName}] 非 JSON 回應：{text} {e}")
                return
            if data.get("success"):
                logging.info(f"創建會員玩家成功{CustomerName} 完成時間{end} CostTime{end-start:.2f}s")
                
            else:
                logging.error(f"觸發失敗{text}")
    except Exception as e:
        logging.error(f"[{CustomerName}] 請求錯誤: {e}")

async def create_wallet(session,customer_id_list):
    
    task=[]
    for customer_id in customer_id_list:
        URL=f"http://10.81.1.21:7001/ac-service-service/resources/accounts/customer/{customer_id}"
        headers = {
                'Content-Type': 'application/json',
                
            }
        payload={
            "creditLimit":0
        }
        task.append(
            session.post(URL,json=payload,headers=headers,ssl=False)
        )
    response=await asyncio.gather(*task, return_exceptions=True)
    print(response)
    

    for customer_id, resp in zip(customer_id_list,response):
        if isinstance(resp, Exception):
            logging.error(f"[{customer_id}] 請求錯誤: {resp}")
            continue
        print("status:", resp.status)
        
        try:
            text=await resp.text()
            data=json.loads(text)
        except Exception as e:
            logging.info(f"[ 非 JSON 回應：{text}{e}")

        if data.get("success"):
            logging.info(f"創建會員錢包成功：{customer_id} ")
            
        else:
            logging.error(f"創建會員錢包失敗{text}")
            
async def Change_Password(session,customer_id_list):
    task=[]
    for customer_id in customer_id_list:
        URL="http://10.81.1.22:7001/tcg-uss-ae/password"

        header={
            "Content-Type":"application/json"
        }
        payload={ 
            "customerId": customer_id, 
            "needLogInToChangePassword": True, 
            "password": "123qwe"
            }
        task.append(
        session.put(URL,json=payload,headers=header,ssl=False)
        )
    resposne=await asyncio.gather(*task, return_exceptions=True)
    for customer_id, resp in zip(customer_id_list,resposne):
        if isinstance(resp, Exception):
            logging.error(f"[{customer_id}] 更改密碼請求錯誤: {resp}")
            continue
        try:
            text=await resp.text()
            data=json.loads(text)
        except Exception:
            logging.error(f"[{customer_id}] 非 JSON 回應: {text}")
            continue
        if data.get("success"):
            logging.info("更改密碼完成")
            return True
        else:
            logging.error(f"更改失敗{text}")
            return False
    
async def create_and_query(session,MerchantCode,name):
    await Create_member(session,name,MerchantCode)
    loop=asyncio.get_running_loop()
    customer_id = await loop.run_in_executor(
        None,
    DB_connect,
    f"(SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='{MerchantCode}@{name}')"
)
    return customer_id
    
async def async_create_main(MerchantCode,username,amount):
   
    member_list=[]
    amount=int(amount)
    for i in range(0,amount+1):
        acount=f"{username}{i}"
        member_list.append(acount)
    async with aiohttp.ClientSession() as session:
        tasks=[
            create_and_query(session,MerchantCode,name)
            for name in member_list
        ]
        id_list=await asyncio.gather(*tasks)
    
        await create_wallet(session,id_list)
        await Change_Password(session,id_list)


