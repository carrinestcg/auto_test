import requests,logging,time,yaml,os,random
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def __init__(self,credential_fe:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential_fe=credential_fe
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login_frontend(credential_fe['username'],credential_fe['password'])
        self.type=''
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
            print(requests_data.text)
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
    
    def Join_promotion(self,promo:int,account:str):
        apply_amount=0
        success_fail=0
        login_URL=f"http://www.sit-gi8viet.com/wps/relay/MCSFE_signUpPromotionJoin"

        headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': 'http://www.sit-gi8viet.com/promotions',
                    'ModuleId': 'DPSTBAS3',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',  
                   
                }
        payload={
                    "promotionId": promo
                }
        cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
                
        response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies,verify=False)
        response_json=response.json()
                
        if response_json.get('success')==True:
                logging.info(f"玩家{account}成功報名")
                apply_amount+=1
                    
        else:
                logging.error(f"玩家{account}報名失敗 已有報名紀錄")
                success_fail+=1
        time.sleep(1)
            
class Backend:
    def header(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/24785",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG",
        }
    def __init__(self,credential_be:str):
        self.session=requests.Session()
        self.credential_be=credential_be
        self.token_expire=None
        self.type=''
        self.token_backend=self.get_token_backend(credential_be['operatorName'],credential_be['password'])
        self.token=self.token_backend
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
    def get_record_id(self,account:str):
    
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-signUpList-search-get"
        
        headers=self.header()
        cookies = {
            "language": "zh_CN"
        }

        params={
            "userName": account,
            "promotionName": "",
            "status": "",
            "pointAmount": 100,
            "pageSize": 10,
            "pageNo": 1,
            "merchantCode": "gi8viet",
        }
        try:
            response=requests.get(API_URL3, cookies=cookies,params=params,headers=headers, verify=False)

            response_data=response.json()
            logging.info(f"完整回應: {response_data}")
            if response_data.get("success") == True:
                record_id_list=response_data.get("value")
                first_record=record_id_list[0]
                record_id=first_record.get("recordId")
                logging.info("拿到recordid")
                return record_id  
            else:
                logging.error("沒有拿到recordid")
                return False
        
        except Exception as e:
            logging.error(f"API呼叫失敗{e}")
    def Approve_to_send_bounus(self,account:str,promo_id:int,record_id:int):
    
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-signUpList-approve-create"
        
        headers=self.header()
        cookies = {
            "language": "zh_CN"
        }

        payload={
            "promotionId": promo_id,
            "configId": 310016,
            "bonusAmount": 100,
            "pointAmount": 100,
            "turnoverMultiplier": 15,
            "minRequiredTo": 1,
            "forAllLabel": "Y",
            "ticketId": 1087007,
            "ticketName": None,
            "ticketType": "CASH_VOUCHER",
            "ticketQuantity": 0,
            "signUpPromotionConfigLabels": None,
            "customerName": account,
            "recordId": record_id,
            "turnoverAmount": "1500.00",
            "bonusBudget": 859888,
            "pointsBudget": 999888,
            "ticketTotalQuantity": 0
        }
        try:
            response=requests.post(API_URL3, cookies=cookies, json=payload,headers=headers, verify=False)

            response_data=response.json()
            if response_data.get("success") == True:
                logging.info("派發手工報名活動成功")
                return True  
            else:
                logging.error("派發手工報名活動失敗")
                return False
        
        except Exception as e:
            logging.error(f"API呼叫失敗{e}")
    
def main():

    password = "123qwe"
    credential_be = {
            "operatorName": "carrine03",
            "password": "Test@1234"
    }
    current_dir=os.path.dirname(__file__)
    yaml_path=os.path.join(current_dir,"config.yaml")
    with open(yaml_path,"r",encoding="utf-8") as f:
        config=yaml.safe_load(f)
    testing_account_list=config.get("testing_account")
    promo_id=4023102
    for account in testing_account_list:
        credential_fe = {
                "username": account,
                "password": password
        }
        try:
            frontend = Frontend(credential_fe)
            if frontend.token:
                frontend.Join_promotion(promo_id,account)
                time.sleep(0.5) 
        except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")    
    try:
        backend=Backend(credential_be)    
        if backend.token:
            for account in testing_account_list:    
                record_id=backend.get_record_id(str(account))
                if record_id:
                    backend.Approve_to_send_bounus(str(account),promo_id,record_id)        
        else:
                logging.error("登入失敗 無法取得Token")
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")

    