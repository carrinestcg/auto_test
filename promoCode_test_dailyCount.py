import requests,logging,time
from datetime import datetime,timedelta
from openpyxl import Workbook
import random,os
from new_register_ap_testi import main

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
    def header(self):
        unit_time=self.unit_time()
        return {
            'Content-Type': 'application/json',
            'X-Timestamp':unit_time,
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'EN',
            'Merchant': 'gi8viet',
            'Origin': 'http://www.sit-gi8viet.com',
            'Referer': 'http://www.sit-gi8viet.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        
    def __init__(self,credential_fe:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential_fe=credential_fe
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login_frontend(credential_fe['username'],credential_fe['password'])
        self.PromoCode_list=''
        self.promoID=''
        self.i=0
        self.record_data_list=''
    def get_token_backend(self,operatorName,password):
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
            "platform": ""
        }
        
        cookies = {
            "language": "zh_CN"
        }
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token
    def get_token_login_frontend(self, username, password):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url='http://www.sit-gi8viet.com/wps/session/login/unsecure'
            
            headers = {
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                
            }
            login_data={
                'username':username,
                'password':password
            } 
            self.username=username
            requests_data=self.session.post(login_url,json=login_data,headers=headers)
            self.username = requests_data.json()['value']['userName']
            self.userid = requests_data.json()['value']['id']
            self.token=requests_data.json()['value']['token']

            self.token_expire=datetime.now()+timedelta(minutes=25)
            return self.token
        
        except requests.RequestException as e:
            logging.error(f"請求失敗{e}")
            return None
    def is_token_valid(self):
        
        return (self.token is not None and 
                self.token_expire is not None and 
                datetime.now() < self.token_expire)
    
    def get_promo_code_list(self):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://www.sit-gi8viet.com/wps/relay/PROMOFE_getPromoCode?_={unit_time}"
        headers=self.header()
        cookies={
            "SHELL_deviceId":"8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966"
        }

        
        response = self.session.get(login_URL, headers=headers,cookies=cookies, verify=False)
        response_json=response.json()

        if response_json.get('success')==True:
            self.PromoCode_list=response_json.get("value",[])
            
        else:
            logging.error(f"沒拿到優惠碼ID")
            return 
    def click_promo_code(self,promoCode):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
        if self.token is None:
            return
        login_URL="http://www.sit-gi8viet.com/wps/relay/PROMOFE_claimPromoCode"
        headers=self.header()
        payload={
             "promoCode": promoCode
        }
        
        cookies = {
            'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
        }
        response = self.session.post(login_URL, headers=headers, json=payload, cookies=cookies, verify=False)
        response_json=response.json()

        if response_json.get('success')==True:
            logging.info(f"領取優惠碼成功")
            return True
        elif response_json.get('success')==False:
            error_message=response_json.get('message')
            logging.error(f"{error_message}")
            return False
    def proccess_all_promoCode(self):
        
        success_count=0
        self.get_promo_code_list()
        for item in self.PromoCode_list:
            promoCode=item.get("promoCode")
            description=item.get("description","")
            if description!='carrine優惠碼':
                continue
            success=self.click_promo_code(promoCode)
            time.sleep(2)
            if success:
                success_count+=1
                logging.info(f"領取第{success_count}組優惠碼成功") 
            else:
                logging.info(f"領取優惠碼失敗") 
                
           
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
    def get_remaincount_promocode(self):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-promotion-promoCode-list"
        params={
            "merchantCode":"gi8viet",
            "status":"A",
            "pageNo":1,
            "pageSize":10
        }
        headers=self.header()
        
        response=requests.get(URL,headers=headers,params=params,verify=False)
        response_json=response.json()
        if response_json.get("success")==True:
            value_list=response_json.get("value",[])
            for item in value_list:
                name=item.get("name","")
                if name=='carrine優惠碼':
                    remainingCountDaily=item.get("remainingCountDaily")
                    remainingCount=item.get("remainingCount")
                    return remainingCountDaily,remainingCount
                
    

def main_():
    
    total_claim_count=0
    dailyremain_count=0
    remainingCount=0
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
        merchantCode='gi8Vnet'
        account_list=main(merchantCode,dailyremain_count)

        for name in account_list:
        #填入玩家帳號
            credential_frontend = {
                "username": name,
                "password": "123qwe"
            }
            try:   
                frontend = Frontend(credential_frontend)
                if frontend.token:
                    logging.info(f"登入成功 Token: {frontend.token}")
                    #frontend.click_promo_code()
                    #schedule.every().day.at(f"{run_time}").do(frontend.click_promo_code,promo)
                    success_count=frontend.proccess_all_promoCode()
                    assert success_count==dailyremain_count
                    logging.info("有確實領取到當日領取上限")
                else:
                    logging.error("登入失敗 無法取得Token")
                    time.sleep(1)
            except Exception as e:
                logging.error(f"前端啟動時發生錯誤: {e}")
        
            
        
            
    except Exception as e:
            logging.error(f"後端啟動時發生錯誤: {e}")
main_()
         

            

    