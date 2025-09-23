import requests,logging,time
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential=credential
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'])
        self.type=''
    def get_token_login(self, username, password):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url='http://www.sit2.sit-gi8viet.com/wps/session/login/unsecure'
            
            headers = {
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
            }
            login_data={
                'username':username,
                'password':password
            } 
            
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
                self.get_token_login(self.credential['username'],self.credential['password'])
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
                self.get_token_login(self.credential['username'],self.credential['password'])
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
                logging.error(f"充值失敗")
                success_fail+=1
            time.sleep(1)
        logging.info(f"總共充值{success_count}筆")
        logging.info(f"總共失敗{success_fail}筆")
        
        
def main(username,password,amount):
        
        #填入玩家帳號
        credential = {
            "username": username,
            "password": password
        }
        try:    
            frontend = Frontend(credential)
            if frontend.token:
                frontend.deposit_QAD(credential['username'],amount)
                frontend.quick_deposit(credential['username'],amount)
                
            else:
                logging.error("登入失敗 無法取得Token")
        
        except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")


    