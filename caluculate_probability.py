import requests
import logging
import time
import random
from datetime import datetime,timedelta
import traceback
import oracledb

import Customer_id

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
        self.merchantCode='gi8viet'
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'])
        self.trans_id=''
        self.configId_1=0
        self.configId_2=0
        self.value_amount=0
        self.reward_count={}
        self.response_list=[]
        self.response_value_list = []
        self.other_prizes_log = []  
        self.rewards = {
        "a": {"id": "1619043", "rate": 80, "min": 3, "max": 10},
        "b": {"id": "1620040", "rate": 20, "min": 20, "max": 30},
        }
        
    def get_token_login(self, username, password):
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
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://www.sit-gi8viet.com/wps/relay/PROMOFE_getClaimTicketList?isApp=N&status=AVAILABLE&_={unit_time}"

        headers={
            'Content-Type': 'application/json',
            'Merchant': 'gi8viet',
            "Authorization":self.token
        }
        
        cookies={
            '_ga': 'GA1.1.343769134.1743155195',
            'SHELL_deviceId': '9248aea2-32ed-4b1a-afa9-d039ed6d1b95',
            '_ga_ABCD123456789': 'GS1.1.1743402506.3.1.1743402698.0.0.0'
        }
        
        response=self.session.get(login_URL,headers=headers,cookies=cookies)
        response.raise_for_status()
        response_json=response.json()
        try:
            if response_json.get('success'):
                self.response_value_list=response_json.get('value',[])
                if self.response_value_list:
                    self.response_value_info=self.response_value_list[0]
                    Trans_id=self.response_value_info.get('transactionId') 
                    Condition_status=self.response_value_info.get('conditionStatus',[])
                    if Trans_id and not Condition_status:
                        self.trans_id=Trans_id
                        logging.info(f"成功拿到交易ID{self.trans_id}")
                        return self.trans_id
                return None
            else:
                logging.error("交易ID查詢失敗")
                return None
        
        except requests.exceptions.RequestException as e:
            logging.error(f"get_Ticket_transaction_ID 失敗: {e}")
        return None
    
    def approve_to_receive_ticket(self,trans_id, customer_id):
        
        login_URL="http://10.81.1.20:7001/promo-fe/resources/ticket/claim"
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        headers={
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            'Connection': 'keep-alive',
            'Language': 'CN',
            'CustomerId':customer_id,
            "CustomerIP":CustomerIP
            
        }
        payload={
                "transactionId": trans_id,
                "isApp": "N"
        }
        
        response=self.session.post(login_URL,headers=headers,json=payload)
        response.raise_for_status()
        response_json=response.json()
        print(response_json)
        try:
            if response_json.get('success'):
                claim_result=response_json.get('value')
                if claim_result:
                    value_amount=claim_result.get('value') 
                    otherPrizes=claim_result.get('otherPrizes',[])
                    self.value_amount=value_amount
                    for item in otherPrizes:
                        configId=item.get('configId')
                        minValue=item.get('minValue')
                        maxValue=item.get('maxValue')
                        self.other_prizes_log.append(otherPrizes) 
                        
                        match = False
                        for key, info in self.rewards.items():
                            if info['min'] <= value_amount <= info['max']:
                                self.reward_count[key] = self.reward_count.get(key, 0) + 1
                                matched = True
                                break
                        if not matched:
                            logging.warning(f"金額 {value_amount} 沒有落在任何設定的區間內")
        
                    logging.info(f"成功領取票卷 交易ID: {self.trans_id} 獎勵 {value_amount} ")
                return True
                
            else:
                logging.error("領取票卷失敗")
                logging.error(traceback.format_exc())
                return False
        except Exception as e:
            logging.error(f"領取票卷失敗{e}")
            logging.error(traceback.format_exc())
            return False
    def poccess_all_ticket(self, customer_id):
        success_count=0
        
        try:
            while True:
                trans_id=self.get_Ticket_transaction_ID()
                if not trans_id:
                    break
                self.approve_to_receive_ticket(trans_id, customer_id)
                success_count+=1
                logging.info(f"領取到第{success_count}次")
                time.sleep(1)
            if success_count == 0:
                logging.warning("沒有成功領取任何票券")
        except KeyboardInterrupt:
            logging.info("手動終止")
        total = sum(self.reward_count.values())
        if total == 0:
            logging.info("沒有成功領取任何票券")
            
        logging.info(f"總共領取 {total} 次票券")
        
        for key, info in self.rewards.items():
            actual_count = self.reward_count.get(key, 0)
            actual_rate = actual_count / total * 100
            expected_rate = info['rate']
            diff = abs(actual_rate - expected_rate)
            status = "OK" if diff <= 15 else "偏差過大"

            logging.info(
                f"[{key}] id={info['id']} 次數={actual_count} "
                f"實際機率={actual_rate:.2f}% 預期rate={expected_rate}% "
                f"差異={diff:.2f}% -> {status}"
            )
            
if __name__ == "__main__":
    from Customer_id import main
    #填入玩家帳號
    credential = {
        "username": "pmp997",
        "password": "123qwe"
    }
    platform = "gi8viet"
    try:    
        customer_id= str(Customer_id.main(username=credential['username'],platform=platform, query_type=1))
        frontend = Frontend(credential)
        if frontend.token:
            logging.info(f"登入成功 Token: {frontend.token}")
            frontend.poccess_all_ticket(customer_id)
            
        else:
            logging.error("登入失敗 無法取得Token")
    
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
        logging.error(traceback.format_exc())

   