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
        
    def approve_to_receive_ticket(self,customer_id):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'], self.credential['Merchant'])
        if self.token is None:
            return
        login_URL=f"http://10.80.1.20:7001/promo-fe/resources/ticket/claim"

        headers={
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'CN',
            'CustomerId':customer_id
            
        }
        payload={
             "transactionId": self.trans_id,
             "isApp": "N"
        }

        
        response=self.session.post(login_URL,headers=headers,json=payload)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success')==True:
            self.response_value_list=response_json.get('value',{})
            if self.response_value_list:
                Type=self.response_value_list.get('type') 
                logging.info(f"成功領取票卷 交易ID: {self.trans_id} 類別{Type}")
            return True
            
        else:
            logging.error(f"領取票卷失敗")
            logging.error(traceback.format_exc())
            return False
    def poccess_all_ticket(self,merchantCode,customer_id):
        success_count=0
        self.merchantCode=merchantCode
        ticket=self.get_Ticket_transaction_ID()
        if not ticket:
            return
        for trans_id in ticket:
            self.trans_id=trans_id
            self.approve_to_receive_ticket(customer_id)
            success_count+=1
            logging.info(f"領取成功")
            time.sleep(1)
class Backend:
    def header(self,platform):
        return{
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_data,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": platform,
            "MerchantCode": platform,
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/311792",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "notPending": "true",
            "platform": "TCG"
        }
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.password=''
        self.merchantCode=credential['Merchant']
        self.token=self.get_token(credential['operatorName'],credential['password'],credential['Merchant'])
        self.credential=credential
        self.token_data=self.token
        self.record_data_list=''
    def get_token(self,operatorName,password,platform):
        login_url="http://sit-admin2.tcg.com/tac/api/login/password"
        payload={
            "operatorName": operatorName,
            "password": password,
            "merchantCode":platform
        }
        headers ={"Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": platform,
            "MerchantCode": platform,
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/311792",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "notPending": "true",
            "platform": "TCG"
        }
        cookies = {
            "language": "zh_CN"
        }
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token
    def search_customerid(self,player:str,platform):
            
            API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/player-search-non-bankcard?merchantCode={platform}&isWildcard=false&sortType=desc&pageable=true&data={player}&searchCode=USERNAME"  
            
            headers=self.header(platform)
            cookies = {
                "language": "zh_CN"
            }
            try:
                response=requests.get(API_URL2, headers=headers, cookies=cookies, verify=False)
                response.raise_for_status()

                response_data=response.json()
                if response_data.get("success") == True:
                    value_data=response_data.get('value',{})
                    player_list=value_data.get('list',[])
                    if player_list:
                        customerId=player_list[0].get("customerId")
                        if customerId:
                            logging.info(f"拿到玩家資訊: {player}")
                            logging.info(f"CustomerID: {customerId}")
                            
                        else:
                            logging.error("沒有拿到CustomerID")
                        return customerId
                    else:
                        logging.error("沒有拿到List")
                    
                else:
                    error_msg = response_data.get("message", "未知錯誤")
                    logging.error(f"未拿到玩家資訊: {error_msg}")
                    return False
            except Exception as e:
                logging.error(f"狀態碼: {response.status_code}")
        

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
    credential_backend = {
        "operatorName": "carrine03",
        "password": "Test@1234",
        "Merchant": merchantCode
    }

    try:    
        backend = Backend(credential_backend)
        if backend.token:
            logging.info(f"登入成功 Token: {backend.token}")
            customer_id=backend.search_customerid(username,merchantCode)
            type_customer_id=str(customer_id)
            frontend = Frontend(credential)
            if frontend.token:
                logging.info(f"登入成功 Token: {frontend.token}")
                frontend.poccess_all_ticket(merchantCode,type_customer_id)
            
            else:
                logging.error("登入失敗 無法取得Token")
        else:
            logging.error("登入失敗 無法取得Token")

        
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")
            logging.error(traceback.format_exc())
