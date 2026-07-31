import requests,logging,schedule,time
from datetime import datetime,timedelta
import threading
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def run_operator(credential, delay=0, barrier=None):
    thread_name=threading.current_thread().name
    if delay:
        logging.info(f"[{thread_name}] 帳號 {credential['username']} 將延遲 {delay:.2f} 秒後登入")
        time.sleep(delay)
 
    logging.info(f"[{thread_name}] 開始處理帳號 {credential['username']}")
    try:    
        frontend = Frontend(credential)
        if frontend.token:
            frontend.get_Ticket_transaction_ID()
            logging.info(f"[{thread_name}] 等待所有帳號都拿到交易ID...")
            barrier.wait(timeout=5) 

            logging.info(f"[{thread_name}] 開始同時領取")
            frontend.approve_to_receive_ticket()
        else:
            logging.error("登入失敗 無法取得Token")
            
    except threading.BrokenBarrierError as e:
        logging.error(f"[{thread_name}] barrier 逾時或中斷: {e}")
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
    
        
class Frontend:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential=credential
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'])
        self.trans_id=''
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
        
        if response_json.get('success')==True:
            self.response_value_list=response_json.get('value',[])
            if self.response_value_list:
                self.response_value_info=self.response_value_list[0]
                self.trans_id=self.response_value_info.get('transactionId')
                logging.info(f"成功拿到交易ID{self.trans_id}")
            return self.trans_id
        else:
            logging.error(f"交易ID查詢失敗")
            return None
        
    def approve_to_receive_ticket(self):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        login_URL=f"http://www.sit-gi8viet.com/wps/relay/PROMOFE_claimTicket"

        headers={
            'Content-Type': 'application/json',
            'Merchant': 'gi8viet',
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'VI',
            'Origin': 'http://www.sit-gi8viet.com',
            'Referer': 'http://www.sit-gi8viet.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        payload={
             "transactionId": self.trans_id,
             "isApp": "N"
        }
        cookies={
            '_ga': 'GA1.1.343769134.1743155195',
            'SHELL_deviceId': '9248aea2-32ed-4b1a-afa9-d039ed6d1b95',
            '_ga_ABCD123456789': 'GS1.1.1743402506.3.1.1743402698.0.0.0'
        }
        
        response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success')==True:
            logging.info(f"成功領取票卷 交易ID: {self.trans_id}")
            
        else:
            logging.error(f"領取票卷失敗")
                
def main(user1, user2):
    credentials = [
        {"username": user1, "password": "123qwe"},
        {"username": user2, "password": "123qwe"}
    ]
    barrier=threading.Barrier(len(credentials))
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(credentials)) as executor:
        futures = []
        for i, credential in enumerate(credentials):
            futures.append(executor.submit(run_operator, credential, i * 1.0, barrier)) 
        for f in concurrent.futures.as_completed(futures):
            try:
                f.result()
            except Exception as e:
                logging.error(f"執行緒發生未預期例外: {e}", exc_info=True)
    logging.info("所有玩家處理完畢")

   