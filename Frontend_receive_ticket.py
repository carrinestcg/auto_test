import requests,logging,time
from datetime import datetime,timedelta
import traceback

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
        self.merchantCode=credential['Merchant']
        self.credential=credential
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'],credential['Merchant'])
        self.trans_id=''
    def get_token_login(self, username, password, merchantCode):
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
                'Merchant':merchantCode
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
    
    def get_Ticket_transaction_ID(self):
        tickets=[]
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'], self.credential['Merchant'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://www.sit-{self.merchantCode}.com/wps/relay/PROMOFE_getClaimTicketList?isApp=N&status=AVAILABLE&_={unit_time}"

        headers={
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            "Authorization":self.token
        }
        
        cookies={
            'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
            'afUserId': '04953ba2-ce16-4b15-8ed4-05c43b9a3153-p',
            'AF_SYNC': '1751265971390'
        }
        
        response=self.session.get(login_URL,headers=headers,cookies=cookies)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success')==True:
            self.response_value_list=response_json.get('value',[])

            if self.response_value_list:
                for item in self.response_value_list:
                    Trans_id=item.get('transactionId') 
                    Condition_status=item.get('conditionStatus',[])
                    if Trans_id and not Condition_status:
                        tickets.append(Trans_id)
                logging.info(f"總共可領{len(tickets)}張")

        else:
            logging.error(f"交易ID查詢失敗")
            
        return tickets
        
    def approve_to_receive_ticket(self):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'], self.credential['Merchant'])
        if self.token is None:
            return
        login_URL=f"http://www.sit-{self.merchantCode}.com/wps/relay/PROMOFE_claimTicket"

        headers={
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'VI',
            'Origin': f'http://www.sit-{self.merchantCode}.com',
            'Referer': f'http://www.sit-{self.merchantCode}.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            
        }
        payload={
             "transactionId": self.trans_id,
             "isApp": "N"
        }
        cookies={
            'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
            'afUserId': '04953ba2-ce16-4b15-8ed4-05c43b9a3153-p',
            'AF_SYNC': '1751265971390'
        }

        
        response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success')==True:
            self.response_value_list=response_json.get('value',{})
            if self.response_value_list:
                Trans_id=self.response_value_list.get('transactionId') 
                Type=self.response_value_list.get('type') 
                logging.info(f"成功領取票卷 交易ID: {self.trans_id} 獎勵 {Trans_id} 類別{Type}")
            return True
            
        else:
            logging.error(f"領取票卷失敗")
            logging.error(traceback.format_exc())
            return False
            
    def poccess_all_ticket(self,merchantCode):
        success_count=0
        self.merchantCode=merchantCode
        ticket=self.get_Ticket_transaction_ID()
        if not ticket:
            return
        for trans_id in ticket:
            self.trans_id=trans_id
            self.approve_to_receive_ticket()
            success_count+=1
            logging.info(f"領取成功")
            time.sleep(1)

def main(username,merchantCode):
    
    if not username:
        logging.info("no UserName")
        return False
    #填入玩家帳號
    credential = {
        "username": username,
        "password": "123qwe",
        "Merchant": merchantCode
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
        logging.error(traceback.format_exc())

