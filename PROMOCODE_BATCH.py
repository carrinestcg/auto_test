import requests
import logging
import time
from datetime import datetime
import random



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def unit_time(self):
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        return unit_time
    def header(self,CustomerId):
        unit_time=self.unit_time()
        return{
            'Content-Type': 'application/json',
            'X-Timestamp':unit_time,
            'Connection': 'keep-alive',
            'Language': 'CN',
            'CustomerId':CustomerId,
            'CustomerIP':'10.180.99.19',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
           
        }
        
    def __init__(self):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.PromoCode_list=''
        self.promoID=''
        self.i=0
        self.record_data_list=''
    
    def get_promo_code_list(self,CustomerId):
        CustomerId=str(CustomerId)
        login_URL="http://10.81.1.20:7001/promo-fe/resources/promo_code"
        headers=self.header(CustomerId)
        
        response = self.session.get(login_URL, headers=headers, verify=False)
        response_json=response.json()

        if response_json.get('success'):
            PromoCode_list=response_json.get("value",[])
            return PromoCode_list
        else:
            logging.error("沒拿到優惠碼ID")
            return 
    def click_promo_code(self,promoCode,CustomerId):
        CustomerId=str(CustomerId)
        login_URL="http://10.81.1.20:7001/promo-fe/resources/promo_code/claim"
        headers=self.header(CustomerId)
        payload={
             "promoCode": promoCode
        }
        
        response = self.session.post(login_URL, headers=headers, json=payload)
        response_json=response.json()
        print(response_json)

        if response.status_code==200:
            logging.info("領取優惠碼成功")
            return True
        else:
            error_message=response_json.get('message')
            logging.error(f"{error_message}")
            return False
    def proccess_all_promoCode(self,customer_id):
        PromoCode_list=self.get_promo_code_list(customer_id)
        success_count=0
        if not PromoCode_list:
            logging.error("優惠碼列表為空，無法領取")
            return 0
        for item in PromoCode_list:
            '''
            promoName=item.get("promoName","")
            if  promoName!='CCD_Promo code_01':
                continue
            '''
            promoCode = item.get("promoCode")
            success=self.click_promo_code(promoCode,customer_id)
            if success:
                success_count+=1
                logging.info(f"領取優惠碼{promoCode}成功") 
            else:
                logging.info("領取優惠碼失敗") 
            
        return success_count
            
class B_end:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.password=''
        self.token=self.get_token(credential['operatorName'],credential['password'])
        self.credential=credential
        self.token_data=self.token
        self.record_data_list=[]
        self.claimid_list=[]
        self.success_count=0
        self.claimid=''
    def header(self):
        return{
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
            "environment": "TCG3",
            "language": "zh_CN",
            "noErrorNotice": "true",
            "platform": "TCG",
            "Tac-Trace-Id":"q02^1XO_0PfgK!xY",
            "Authorization": self.token_data,
        }
    def get_token(self,operatorName,password):
        login_url="http://sit-admin2.tcg.com/tac/api/login/password"
        payload={
                "operatorName": operatorName,
                "password": password
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
            "platform": "",
            "Tac-Trace-Id":"&kZEwhHNN!Pe(Qj_"
        }
        
        cookies = {
            "language": "zh_CN",
            "JSESSIONID":"wK3EQfljeUHXxYAN8uKQcvkpKBg1WM4PaVshMx7TpsBoHDtAk4c_!-1653539373"
        }
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token
    def get_remaincount_promocode(self,):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-promotion-promoCode-list"
        params={
            "merchantCode":"gi8viet",
            "status":"A",
            "pageNo":1,
            "pageSize":1000
        }
        headers=self.header()
        cookies = {
            "language": "zh_CN",
        }
        response=requests.get(URL,headers=headers,params=params,cookies=cookies,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            value_list=response_json.get("value",[])
            for item in value_list:
                name=item.get("name","")
                if name=='TCG-142327':
                    remainingCountDaily=item.get("remainingCountDaily")
                    remainingCount=item.get("remainingCount")
                    return remainingCountDaily,remainingCount  
            else:
                logging.error("找不到指定優惠碼名稱")
                return None,None
                
        else:
            logging.error("查詢剩餘次數失敗")
            return None,None

def main(username:str):
    from Customer_id import main
    total_claim_count=0
    dailyremain_count=0
    remainingCount=0
    success_count=0
    credential_Backend = {
            "operatorName": "carrine03",
            "password": "Test@1234"
        }
    
    try:    
        backend = B_end(credential_Backend)
        if backend.token:
            dailyremain_count,remainingCount=backend.get_remaincount_promocode()
            logging.info(f"當日剩餘次數{dailyremain_count}")
            logging.info(f"總剩餘次數{remainingCount}")

        
        try:   
            frontend = Frontend()
            customer_id=main(username,platform="gi8viet",query_type=1)
            success_count=frontend.proccess_all_promoCode(customer_id)
            total_claim_count+=success_count
        
        except Exception as e:
                logging.error(f"啟動時發生錯誤: {e}")
        time.sleep(0.5)
        
        if backend.token:
            after_receive_remain_dailyremain_count,after_receive_remainingCount=backend.get_remaincount_promocode()
            logging.info(f"更新後的當日剩餘次數{after_receive_remain_dailyremain_count}")
            logging.info(f"總剩餘次數{remainingCount}")
            if (dailyremain_count-after_receive_remain_dailyremain_count)==total_claim_count:
                logging.info("當日剩餘次數扣除正確")
            else:
                logging.error("當日剩餘次數扣除不正確")
            if (remainingCount-after_receive_remainingCount)==total_claim_count:
                logging.info("總剩餘次數扣除正確")
            else:
                logging.error("總剩餘次數扣除不正確")
            
        if success_count > 0:
            return after_receive_remain_dailyremain_count, after_receive_remainingCount,success_count
        else:
            logging.info("沒有成功領取任何優惠碼")
            return dailyremain_count, remainingCount, success_count
            
        
            
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")
            return None, None, None
         

    
            

    