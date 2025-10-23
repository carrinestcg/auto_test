import requests,logging,time,yaml,os
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from deposit_api import batch_approve

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def unit_time():
    current_time=datetime.now()
    unit_time=str(int(current_time.timestamp()*1000))
    return unit_time

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
    
    def unitTime(self):
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        return unit_time
    
    def header(self):
        unitTime=self.unitTime()
        return {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9',
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                "Authorization":self.token,
                'Connection': 'keep-alive',
                'Language': 'EN',
                'Origin': 'http://www.sit-gi8viet.com',
                'Referer': 'http://www.sit-gi8viet.com/',
                'ModuleId': 'DPSTBAS3',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',  
                'x-timestamp': unitTime     
            }
    def deposit_QAD(self,username,amount):
        success_fail=0
        success_count=0
        bank_codes=["MWQR","Alipay","EWBANK123","TCG-106324 depositByQRImageUrl"]
        bank_types=["MWQR","MAQR","QQ","WCFQR","ALIFQR","KAMI"]
        vender_id=[28886,28906,21306,28268,28268,28268]
        while len(bank_codes) < len(bank_types):
            bank_codes.append(bank_codes[-1])
        for bank_code, bank_type, vender in zip(bank_codes, bank_types, vender_id):
            if not self.is_token_valid():
                logging.info("token 過期, 重新登入")
                self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
            if self.token is None:
                return
            login_URL=f"http://www.sit-gi8viet.com/wps/relay/MCSFE_depositByQRImageUrl"

            headers=self.header()
            payload={
                "targetUsername": username,
                "amount":amount,
                "bankCode":bank_code,
                "bankType":bank_type, 
                "showQrImageOnly":1,
                "vendorId":vender,
                "mcsBankCode":bank_type,
                "deviceId": "cc688917-11c4-34c5-aeb6-bbf37742f679",
                "token":self.token
            }
            cookies={
                'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
            }
            
            response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies,verify=False)
            response_json=response.json()
            
            if response_json.get('success')==True:
                logging.info(f"成功充值 交易ID")
                success_count+=1
                
            else:
                print(response_json)
                logging.error(f"充值失敗")
                success_fail+=1
            time.sleep(1)
        logging.info(f"總共充值{success_count}筆")
        logging.info(f"總共失敗{success_fail}筆")
            
    def quick_deposit(self,username,amount):
        success_fail=0
        success_count=0
        bank_types=["null"]
        bank_codes=["TCG-106324"]
        for bank_type, bank_code in zip(bank_types,bank_codes):
            if not self.is_token_valid():
                logging.info("token 過期, 重新登入")
                self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
            if self.token is None:
                return
            login_URL=f"http://www.sit-gi8viet.com/wps/relay/MCSFE_manualTransferByAccountName"

            headers=self.header()
            payload={
                "targetUsername": username,
                "payeeName":"bbbb",
                "amount":amount,
                "bankCode":bank_type,
                "vendorId":28166,
                "mcsBankCode":bank_code,
                "token":self.token
            }
            cookies={
                'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
            }
            
            response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies,verify=False)
            response_json=response.json()
            
            if response_json.get('success')==True:
                logging.info(f"成功充值 交易ID")
                success_count+=1
                
            else:
                print(response_json)
                logging.error(f"充值失敗")
                success_fail+=1
            time.sleep(1)
        logging.info(f"總共充值{success_count}筆")
        logging.info(f"總共失敗{success_fail}筆")
        
    
class Backend:
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
    def Bonus_record_page(self):
            
            API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-v2-promotionClaim-search?pageSize=20&pageNo=1"  
            start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
            end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
            headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": self.token,
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Language": "zh_CN",
                "Merchant": "gi8viet",
                "MerchantCode": "gi8viet",
                "Tac-Trace-Id":"2eAM8QMqpfEd3QxE",
                "Referer": "http://sit-admin2.tcg.com/311792",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "environment": "TCG3",
                "merchantCode": "gi8viet",
                "notPending": "true",
                "platform": "TCG"
            }
            payload={
                "fromDate":start_time,
                "toDate":end_time,
                "isFuzzySearch":True,
                "searchDateMode":"requestedTimeSearch",
                "merchantCode":"gi8viet",

            }
            cookies = {
                "language": "zh_CN",
            }
            try:
                response=requests.get(API_URL2, headers=headers, params=payload, cookies=cookies, verify=False)

                response_data=response.json()
                if response_data.get("success") == True:
                    self.record_data_list=response_data.get('value',[])
                    return True
                else:
                    response_data.get("message", "未知錯誤")
                    return False
                
            except Exception as e:
                logging.error(f"狀態碼: {response.status_code}")

    create_record=[]
    
            
        
def main(usernames:list,password):
    from deposit_api import batch_approve
    from deposit_count import implement_function
    from accumulated_deposit import implement_accumulated_function
    merchantCode="gi8viet"
    username_1=usernames[0]
    username_2=usernames[1]
    credential_fe = {
            "username": username_1,
            "password": password
    }
    credential_fe_for_accu = {
            "username": username_2,
            "password": password
    }
    credential_be = {
            "operatorName": "carrine03",
            "password": "Test@1234"
    }
    current_dir=os.path.dirname(__file__)
    yaml_path=os.path.join(current_dir,"config.yaml")
    with open(yaml_path,"r",encoding="utf-8") as f:
        config=yaml.safe_load(f)
    promotion_id_for_deposit=config.get("promotion_ids_for_deposit_2",[])
    try:
        backend=Backend(credential_be)
        frontend = Frontend(credential_fe)
        if backend.token:
            logging.info("backend class有成功運作")
            deposit_count=implement_function(username_1)
            print(deposit_count)
            if deposit_count>5:
                promo=promotion_id_for_deposit[5]
                if frontend.token:
                        frontend.deposit_QAD(credential_fe['username'],promo)
                        #frontend.deposit_TBQR(credential_fe['username'])
                else:
                    logging.error("登入失敗 無法取得Token")
                batch_approve(merchantCode)    
            else:  
                available_for_deposit_promo=promotion_id_for_deposit[deposit_count:]
                for promo in available_for_deposit_promo:
                    frontend = Frontend(credential_fe)
                    if frontend.token:
                            frontend.deposit_QAD(credential_fe['username'],promo)
                            time.sleep(1)
                            batch_approve(merchantCode) 
                            time.sleep(0.5)
                                #frontend.deposit_TBQR(credential_fe['username'])
                                #frontend.quick_deposit(credential_fe['username'])
                    else:
                        logging.error("登入失敗 無法取得Token")
            #額外執行一個累計次數存款        
            if frontend.token:
                            promo=4023093
                            accumulated_time=implement_accumulated_function()
                            for _ in range(accumulated_time):
                                frontend.deposit_QAD(credential_fe_for_accu['username'],promo)
                            batch_approve()

        else:
            logging.error(f"沒有拿到後台token:")        
            #backend.Bonus_record_page()  --之後再修改 
  
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")


    