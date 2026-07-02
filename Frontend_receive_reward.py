import requests
import logging
import time
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
        self.merchantCode=credential['merchantCode']
        self.credential=credential
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'],credential['merchantCode'])
        self.reward_id=''
        self.promotion_type=''
    def get_token_login(self, username, password,merchantCode):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url=f'http://www.sit-{self.merchantCode}.com/wps/session/login/unsecure'
            
            headers = {
                'Content-Type': 'application/json',
                'Merchant': self.merchantCode,
            }
            login_data={
                'username':username,
                'password':password,
                'merchantCode':merchantCode
            } 
            
            requests_data=self.session.post(login_url,json=login_data,headers=headers)
            print(requests_data.text)
            self.username = requests_data.json()['value']['userName']
            self.userid = requests_data.json()['value']['id']
            self.token=requests_data.json()['value']['token']

            self.token_expire=datetime.now()+timedelta(minutes=25)
            logging.info(f"token 將在{self.token_expire}過期 ")
            return self.token
        
        except requests.RequestException as e:
            logging.error(f"請求失敗{e}")
            return None
    def is_token_valid(self):
        
        return (self.token is not None and 
                self.token_expire is not None and 
                datetime.now() < self.token_expire)
    
    def get_Cliam_ID(self):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        
        Claim_ID=[]
        promotionType_list=[]
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://sit-{self.merchantCode}.com/wps/relay/PROMOFE_getPromoList&_={unit_time}"


        headers={
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            "Authorization":self.token,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        cookies = {
            'afUserId': '04953ba2-ce16-4b15-8ed4-05c43b9a3153-p',
            'AF_SYNC': '1749612572405',
            'SHELL_deviceId': '45fcebb4-8393-f955-97e3-9820a7899b78'
        }
        
        response=self.session.get(login_URL,headers=headers,cookies=cookies,verify=False)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success'):
            self.response_value_list=response_json.get('value',[])
            if self.response_value_list:
                for item in self.response_value_list:
                    claimId=item.get('claimId') 
                    promotionType=item.get('promotionType')
                    if claimId and promotionType:
                        Claim_ID.append(claimId)
                        promotionType_list.append(promotionType)

                logging.info(f"總共可領{len(Claim_ID)}個獎勵")
            else:
                logging.info("目前沒有獎勵可領取")
            
        else:
            logging.error("交易ID查詢失敗")
            
        return Claim_ID,promotionType_list
        
    def approve_to_receive(self):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://sit-{self.merchantCode}.com/wps/relay/MCSFE_claimIssuedPromotion"

        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'EN',
            'Origin': f'https://sit4.sit-{self.merchantCode}.com',
            'Referer': f'https://sit4.sit-{self.merchantCode}.com/',
            'sec-ch-ua-mobile': '?0',
            "moduleid": "REWCEN3",
            'sec-ch-ua':'"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',  
            'x-timestamp': unit_time     
        }
        payload={
            "promotionClaimId": self.reward_id,
            "promotionType": self.promotion_type
        }
        cookies={
            'SHELL_deviceId': '81787dd4-3200-e7f3-5da9-bcd3a92fe636',
        }
        
        response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies,verify=False)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success'):
            logging.info(f"成功領取獎勵 交易ID: {self.reward_id}")
            return True
            
        else:
            logging.error(f"領取票卷失敗{response_json}")
            return False
            
    def poccess_all_ticket(self,merchantCode):
        success_count=0
        self.merchantCode=merchantCode
        Claim_ID,promotionType_list=self.get_Cliam_ID()
        if not Claim_ID:
            return
        for reward_id,PromoType in zip(Claim_ID,promotionType_list):
            self.reward_id=reward_id
            self.promotion_type=PromoType
            self.approve_to_receive()
            success_count+=1
            logging.info("領取成功")
            time.sleep(1)

def main(username,merchantCode):
  
    #填入玩家帳號
    credential = {
        "username": username,
        "password": "123qwe",
        "merchantCode":merchantCode
    }
    try:    
        frontend = Frontend(credential)
        if frontend.token:
            logging.info(f"登入成功 Token: {frontend.token}")
            frontend.poccess_all_ticket(merchantCode)
            
        else:
            logging.error("登入失敗 無法取得Token")
    
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")





   