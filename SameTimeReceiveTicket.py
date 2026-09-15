import requests,logging,schedule,time
from datetime import datetime,timedelta
import threading
import concurrent.futures
from Customer_id import main as get_customer_id

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def _result(username, success, message, **extra):
    row = {
        "username": username,
        "success": bool(success),
        "message": message or "",
        "ticket_type": extra.get("ticket_type") or "",
        "trans_id": extra.get("trans_id") or "",
    }
    return row


def run_operator(credential, delay=0, barrier=None):
    thread_name=threading.current_thread().name
    username = credential.get("username") or ""
    if delay:
        logging.info(f"[{thread_name}] 帳號 {username} 將延遲 {delay:.2f} 秒後登入")
        time.sleep(delay)
 
    logging.info(f"[{thread_name}] 開始處理帳號 {username}")
    try:    
        frontend = Frontend(credential)
        if not frontend.token:
            logging.error("登入失敗 無法取得Token")
            return _result(username, False, "登入失敗，無法取得 Token")
        ticket = frontend.get_Ticket_transaction_ID(credential['merchantCode'], credential['username'])
        logging.info(f"[{thread_name}] 等待所有帳號都拿到交易ID...")
        if barrier is not None:
            barrier.wait(timeout=5)

        logging.info(f"[{thread_name}] 開始同時領取")
        logging.info(f"[{thread_name}] DEBUG trans_id={frontend.trans_id!r}, ticket={ticket!r}")
        if not ticket or not frontend.trans_id:
            return _result(username, False, "找不到可領取票券（無 transactionId）")
        ticket_type = ticket.get(frontend.trans_id) or ""
        if ticket_type == "SLOT_MACHINE":
            claim_out = frontend.approve_to_receive_Slot_ticket(frontend.trans_id)
        else:
            claim_out = frontend.approve_to_receive_ticket(frontend.trans_id)
        if isinstance(claim_out, tuple):
            ok = bool(claim_out[0])
            detail = claim_out[1] if len(claim_out) > 1 else ""
        else:
            ok, detail = bool(claim_out), ""
        return _result(
            username,
            ok,
            detail or ("領取成功" if ok else "領取失敗"),
            ticket_type=ticket_type,
            trans_id=frontend.trans_id,
        )
            
    except threading.BrokenBarrierError as e:
        logging.error(f"[{thread_name}] barrier 逾時或中斷: {e}")
        return _result(username, False, f"barrier 逾時或中斷: {e}")
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
        return _result(username, False, f"執行錯誤: {e}")
    
        
class Frontend:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.customer_id = None 
        self.credential=credential
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'])
        self.trans_id=''
    def get_token_login(self, username, password):
        
        if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
            return self.token
        
        login_url='http://sit14.sit-gi8viet.com/wps/session/login/unsecure'
        
        headers = {
            'Content-Type': 'application/json',
            'Merchant': 'gi8viet',
            
        }
        login_data={
            'username':username,
            'password':password
        } 
        try:
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
        except (KeyError, ValueError) as e:
            logging.error(f"登入回應解析失敗 帳號={username}: {e}")
            return None
    
        
    def is_token_valid(self):
        
        return (self.token is not None and 
                self.token_expire is not None and 
                datetime.now() < self.token_expire)
    
    def get_Ticket_transaction_ID(self, merchantCode, username):
        ticket={}
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://10.81.1.20:7001/promo-fe/resources/ticket/list"
        self.customer_id=get_customer_id(username, merchantCode, 1)
        self.customer_id=str(self.customer_id)
        headers={
            'Content-Type': 'application/json',
            'Language': 'CN',
            "CustomerId":self.customer_id
        }
        response=self.session.get(login_URL,headers=headers)
        response.raise_for_status()
        response_json=response.json()
        
        if response_json.get('success')==True:
            self.response_value_list=response_json.get('value',[])
            if self.response_value_list:
                for item in self.response_value_list:
                    Type=item.get('type')
                    if Type=="SLOT_MACHINE" or Type=="PRIZE_WHEEL":
                        Trans_id=item.get('transactionId')
                        if Trans_id:
                            ticket[Trans_id] = Type
                            if not self.trans_id:          # 只記錄第一筆
                                self.trans_id = Trans_id
                logging.info(f"成功拿到交易ID{list(ticket.keys())}")
            return ticket
        else:
            logging.error(f"交易ID查詢失敗")
            return None
        
    def approve_to_receive_ticket(self, trans_id):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return False, "Token 無效，無法領取"
        login_URL=f"http://sit14.sit-gi8viet.com/wps/relay/PROMOFE_claimTicket"

        headers={
            'Content-Type': 'application/json',
            'Merchant': 'gi8viet',
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'VI',
            'Origin': 'http://sit14.sit-gi8viet.com',
            'Referer': 'http://sit14.sit-gi8viet.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        }
        payload={
             "transactionId": trans_id,
             "isApp": "N"
        }
        cookies={
            '_ga': 'GA1.1.343769134.1743155195',
            'SHELL_deviceId': '9248aea2-32ed-4b1a-afa9-d039ed6d1b95',
            '_ga_ABCD123456789': 'GS1.1.1743402506.3.1.1743402698.0.0.0'
        }
        
        response=self.session.post(login_URL,headers=headers,json=payload,cookies=cookies)
        if response.status_code != 200:
            logging.error(f"[{self.credential.get('username')}] 領取票卷 HTTP {response.status_code}, trans_id={trans_id}, body={response.text}")
            return False, f"HTTP {response.status_code}"
        
        response_json=response.json()
        
        if response_json.get('success')==True:
            logging.info(f"[{self.credential.get('username')}] 成功領取票卷 交易ID: {trans_id} ")
            return True, "領取成功"
        err = response_json.get("message") or "領取失敗"
        logging.error(f"[{self.credential.get('username')}] 領取票卷失敗: {err}")
        return False, err

    def approve_to_receive_Slot_ticket(self,trans_id):
        #http://sit14.sit-gi8viet.com/wps/relay/PROMOFE_spinSlotMachine
        login_URL="http://10.81.1.20:7001/promo-fe/resources/slot_machine/spin"
        headers={
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Language': 'CN',
            'CustomerId':self.customer_id
            
        }
        payload={
                "transactionId": trans_id,
                "isApp": "N"
        }

        
        response=self.session.post(login_URL,headers=headers,json=payload)
        if response.status_code != 200:
            logging.error(f"[{self.credential.get('username')}] 領取票卷 HTTP {response.status_code}, trans_id={trans_id}, body={response.text}")
            return False, f"HTTP {response.status_code}"
        response_json=response.json()
        logging.info(f"[{self.credential.get('username')}] response={response_json}") 
        if response_json.get('success'):
            self.response_value_list=response_json.get('value',{})
            Type = ""
            if self.response_value_list:
                Type=self.response_value_list.get('rewardType') 
                logging.info(f"[{self.credential.get('username')}] 成功領取票卷 交易ID: {trans_id} 類別{Type}")
            return True, f"水果機 spin 成功{(' 類別 ' + str(Type)) if Type else ''}"
            
        elif not response_json.get('success') and response_json.get('message') == "slot_machine_use_claim_for_final_spin":
            logging.error("水果機最後一次需打原先領取API")
            ok, detail = self.approve_to_receive_ticket(trans_id)
            if ok:
                return True, "最後一轉改 CLAIM 成功"
            return False, detail or "最後一轉 CLAIM 失敗"
        err = response_json.get("message") or "水果機領取失敗"
        logging.error(f"[{self.credential.get('username')}] 領取票卷失敗: {err}")
        return False, err

def main(user1, user2):
    credentials = [
        {"username": user1, "password": "123qwe", "merchantCode": "gi8viet"},
        {"username": user2, "password": "123qwe", "merchantCode": "gi8viet"}
    ]
    barrier=threading.Barrier(len(credentials))
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(credentials)) as executor:
        futures = []
        for i, credential in enumerate(credentials):
            futures.append(executor.submit(run_operator, credential, i * 1.0, barrier)) 
        for f in concurrent.futures.as_completed(futures):
            try:
                row = f.result()
                if row:
                    results.append(row)
            except Exception as e:
                logging.error(f"執行緒發生未預期例外: {e}", exc_info=True)
                results.append(_result("", False, f"執行緒例外: {e}"))
    logging.info("所有玩家處理完畢")
    success_count = sum(1 for r in results if r.get("success"))
    fail_count = len(results) - success_count
    overall_ok = len(results) > 0 and fail_count < len(results)
    if success_count == 1 and fail_count == 1:
        verdict = "符合同時領取預期（一人成功、一人失敗）"
        overall_ok = True
    elif success_count >= 2:
        verdict = "兩人皆領取成功（請確認是否為同一庫存／同一張券）"
    elif success_count == 0:
        verdict = "兩人皆領取失敗"
        overall_ok = False
    else:
        verdict = f"成功 {success_count}、失敗 {fail_count}"
    return {
        "kind": "same_time_receive_ticket",
        "success": overall_ok,
        "message": verdict,
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
    }

   