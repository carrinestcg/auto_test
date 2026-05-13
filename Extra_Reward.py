import time
import requests
import logging
import json
from datetime import datetime,timedelta
import traceback
from DB_connect import DB_connect
import random
from deposit_api import batch_approve

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def _same_id(a, b):
    """比對 promotionId／ticketId：API 常為 int，JSON／表單常為 str。"""
    if a is None or b is None:
        return False
    try:
        return int(a) == int(b)
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def _ticket_id_wanted_set(ticket_id_list):
    """將前端傳入的票券 ID 轉成可比對的 str 集合（避免 ticket_ID in ticket_id_list 型別不一致）。"""
    if not ticket_id_list:
        return set()
    out = set()
    for x in ticket_id_list:
        if x is None:
            continue
        s = str(x).strip()
        if s:
            out.add(s)
    return out


'''呼叫翻倍API'''
def get_claim_id(CustomerId,promotionId):
    claim_id_list=[]
    try:
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        URL="http://10.80.1.19:8084/promo-fe/resources/extra_reward/claim_list/unapplied"
        header={
            "accept":"application/json",
            "CustomerIP":CustomerIP,
            "CustomerId":CustomerId
        }
        print(promotionId)
        response=requests.get(URL,headers=header,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            value=response_json.get("value")
            claim_list=value.get("claims",[])
            if not claim_list:
                logging.error(
                    "拿到空 cliam_list（value keys: %s）",
                    list(value.keys()) if isinstance(value, dict) else value,
                )
                return None
            else :
                for promo in claim_list:
                    if _same_id(promo.get("promotionId"), promotionId):
                        claim_id=promo.get("claimId")
                        if claim_id is not None:
                            logging.info(f"拿到cliam_id:{claim_id}")
                            claim_id_list.append(claim_id)
                        
                        else:
                            logging.error("沒有拿到cliam_id")
                            continue
                        
                if not claim_id_list:
                    logging.error("沒有找到符合的 claim_id")
                    return None
                    
                return claim_id_list
        else:
            logging.error("呼腳失敗")
            
    except Exception as e:
            logging.error(f"系統錯誤{e}")

'''後端派發＆審核票券流程'''
class Backend:
    def __init__(self, credential:dict):
        self.credential=credential
        self.token=self.get_token()
        
    def get_token(self):
        login_url="http://sit-admin2.tcg.com/tac/api/login/password"
        payload={
           "operatorName": self.credential['operatorName'],
            "password": self.credential['password']
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
        requests_data.raise_for_status()
        token_data=requests_data.json()
        return token_data.get("token")

    def create_bonus(self,player:str,bonusAmount:int,bonusPointAmount:int,ticketId_list:list,ticketQuantity:int,prmotion_id:int):
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/mcs-manual-promotion-addManualPromotionClaim?" 
        for ticketId in ticketId_list:
            payload = {
            "merchantCode": "gi8viet",
            "customerName": player,
            "bonusAmount": bonusAmount,
            "bonusPointAmount": bonusPointAmount,
            "promotionId": prmotion_id,
            "toReqAmount": 0,
            "ticketId": ticketId,
            "ticketQuantity": ticketQuantity
        }

            headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/24785",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "platform": "TCG"
            }
            cookies = {
                "language": "zh_CN"
            }
            try:
                response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
                response.raise_for_status()
                
                
                response_data = response.json()
                
                
                if response_data.get("success") :
                    logging.info("手動紅利發放成功 ")
                    
                else:
                    error_msg = response_data.get("message", "未知錯誤")
                    logging.error(f"手動紅利發放失敗: {error_msg}")
                    return False
                    
            except requests.RequestException as e:
                logging.error(f"HTTP錯誤 {e}")
                return False
            except ValueError as e:
                logging.error(f"JSON解析錯誤: {e}")
                return False
            except Exception as e:
                logging.error(f"其他錯誤: {e}")
                return False
        return True
    
    def Search_Customer_bonus(self,player:str):
      
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/get/mcs-manualPromotion-search" 
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        payload = {
        "merchantCode": "gi8viet",
        "status": "P",
        "customerName":player,
        "searchDateMode": "issuedDateSearch",
        "startTime": start_time,
        "endTime": end_time,
        "pageSize": 10,
        "pageNo": 1
    }

        headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": self.token,
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Language": "zh_CN",
        "Merchant": "gi8viet",
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/24785",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "TCG3",
        "merchantCode": "gi8viet",
        "platform": "TCG"
        }
        cookies = {
            "language": "zh_CN"
        }
        try:
            response = requests.get(API_URL, params=payload, headers=headers, cookies=cookies, verify=False)
            response.raise_for_status()
            
            response_data = response.json()
            
            if response_data.get("success"):
                customer_list=response_data.get("value",[])
                
                if not customer_list:
                    logging.error("回應中找不到 customerlist")
                    return []
                
                claimid_list = []
                for customer_info in customer_list:
                    claimid = customer_info.get("id")
                    promotion_type = customer_info.get("promotionType")
                    if claimid:
                        claimid_list.append({
                            "promoClaimId": claimid,
                            "promotionType": promotion_type
                        })
                return claimid_list
                
            else:
                    logging.error("回應中找不到 customerId 或 claimid")
                    return None, None, None
            
                
        except requests.RequestException as e:
            logging.error(f"HTTP錯誤 {e}")
            return None, None, None
        except ValueError as e:
            logging.error(f"JSON解析錯誤: {e}")
            return None, None, None
        except Exception as e:
            logging.error(f"其他錯誤: {e}")
            return None, None, None
    def Confirm_Customer_bonus(self, claimid_list ):
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/mcs-manual-promotion-batchApproveRejectManualPromotion" 
        payload = {
            "status": "I",
            "promotionClaims": claimid_list
        }
    
        headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": self.token,
        "Connection": "keep-alive",
        "Language": "zh_CN",
        "Merchant": "gi8viet",
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/24785",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "TCG3",
        "merchantCode": "gi8viet",
        "platform": "TCG"
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers=headers, verify=False)
            response.raise_for_status()
            logging.info(claimid_list)
            response_data = response.json()
            if response_data.get("success") :
                logging.info("批量審核活動紅利成功 ")
                return True
            else:
                error_msg = response_data.get("value")
                logging.error(f"未審核成功 value: {error_msg}")
                return False
                
        except requests.RequestException as e:
            logging.error(f"HTTP錯誤 {e}")
            return False
        except ValueError as e:
            logging.error(f"JSON解析錯誤: {e}")
            return False
        except Exception as e:
            logging.error(f"其他錯誤: {e}")
            return False
        
'''前端領取票券流程'''
class Frontend:
    def __init__(self,credential_fe:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential=credential_fe
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential_fe['username'],credential_fe['password'])
        self.type=''
        self.trans=''
    def get_token_login(self, username, password):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url='http://www.sit6.sit-gi8viet2.com/wps/session/login/unsecure'
            
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
        
    def get_Ticket_transaction_ID(self,merchantCode,username, ticket_id_list:list):
        transID_list=[]
        wanted = _ticket_id_wanted_set(ticket_id_list)
        if not wanted:
            logging.warning("ticket_id_list 為空，無法對應 transactionId")
            return []
        login_URL="http://10.80.1.20:7001/promo-fe/resources/ticket/list"
        parmas={
            
            "status":"AVAILABLE",
            "isAll":"N",
            
        }
        self.customer_id=DB_connect(f"SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='gi8viet@{username}'")
        headers={
            'Content-Type': 'application/json',
            'Merchant': merchantCode,
            'Language':"CN",
            'CustomerId':self.customer_id
        }
        
        response=self.session.get(login_URL,headers=headers,params=parmas, verify=False)
        response_json=response.json()
        
        if response_json.get('success'):
            self.response_value_list=response_json.get('value',[])

            if self.response_value_list:
                for item in self.response_value_list:
                    ticket_ID=item.get('ticketId')
                    if ticket_ID is None:
                        continue
                    if str(ticket_ID).strip() not in wanted:
                        continue
                    logging.info(f"匹配到票券: ticketId={ticket_ID}, type={item.get('type')}, status={item.get('status')}, 完整={item}")
                    Trans_id=item.get('transactionId')
                    if Trans_id:
                        transID_list.append(Trans_id)
                    else:
                        logging.warning(f"ticketId {ticket_ID} 沒有 transactionId，跳過")
                        continue
                if not transID_list:
                    api_ids = [item.get("ticketId") for item in self.response_value_list]
                    logging.error(
                        "票券列表中找不到與輸入相符的 ticketId。輸入=%s，API 回傳的 ticketId 範例=%s",
                        sorted(wanted),
                        api_ids[:20],
                    )
                return transID_list
            logging.warning("ticket/list 的 value 為空")
            return []
        else:
            logging.error("交易ID查詢失敗")
        return []
    def approve_to_receive_ticket(self, trans_id_list:list):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        if not trans_id_list:
            logging.warning("transactionId 列表為空，略過領取票券")
            return
        login_URL="http://www.sit6.sit-gi8viet2.com/wps/relay/PROMOFE_claimTicket"
        for Trans in trans_id_list:
            headers={
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                "Authorization":self.token,
                'Connection': 'keep-alive',
                'Language': 'VI',
                'Origin': 'http://www.sit6.sit-gi8viet.com',
                'Referer': 'http://www.sit6.sit-gi8viet.com/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                
            }
            payload={
                "transactionId": Trans,
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
            logging.info(f"claimTicket 完整回應: {response_json}") 
            
            if response_json.get('success'):
                self.response_value_list=response_json.get('value',{})
                if self.response_value_list:
                    Trans_id=self.response_value_list.get('transactionId') 
                    Type=self.response_value_list.get('type') 
                    logging.info(f"成功領取票卷 交易ID: {Trans_id}  類別{Type}")
                
            else:
                logging.error("領取票卷失敗")
                logging.error(traceback.format_exc())
                return False
            
        return True
            
    '''觸發翻倍充值流程'''
    def deposit_QAD(self,username,amount,promotionId):
        success_fail=0
        success_count=0

        
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login(self.credential['username'],self.credential['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        
        login_URL="http://www.sit3.sit-gi8viet2.com/wps/relay/MCSFE_depositByQRImageUrl"

        headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Merchant': 'gi8viet',
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'EN',
            'Referer': 'http://www.sit-gi8viet.com/',
            'ModuleId': 'DPSTBAS3',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',  
            'x-timestamp': unit_time     
        }
        customer_id=DB_connect(f"SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='gi8viet@{username}'")
        promoClaimId_list=get_claim_id(customer_id,promotionId)
        if not promoClaimId_list:
            logging.error("無法取得 claim_id_list，跳過此次充值")
            return 0
        for claim in promoClaimId_list:
            print(claim)
            payload={
                "targetUsername": username,
                "amount":amount,
                "bankCode": "MWQR",
                "bankType": "MWQR",
                "showQrImageOnly":1,
                "vendorId":28886,
                "deviceId": "88493739-ff27-4ebc-80ad-2dcc88086435",
                "mcsBankCode": "WECHATTHB",
                "token":self.token,
                "nickname": "1",
                "promotionId":promotionId,
                "promoClaimId":claim
            }
            
            
            response=self.session.post(login_URL,headers=headers,json=payload,verify=False)
            response_json=response.json()
            
            if response_json.get('success'):
                logging.info("成功充值 交易ID")
                success_count+=1
                
            else:
                logging.error(f"充值失敗{response.text}")
                success_fail+=1
            time.sleep(1)
        return success_count


'''主程式'''
def main(username, ticket_id_list:list, ticketQuantity, promotion_id, amount, Extra_Promo_ID):
    password_fe = "123qwe"
    claimid_list=[]
    merchantCode='gi8viet'
    credential_fe = {
            "username": username,
            "password": password_fe
        }
    
    credential_be = {
        "operatorName": "carrine03",
        "password": "Test@1234"
        }
    bonus=5
    point=0
    try:
        backend=Backend(credential_be)
        if backend.token:
            backend.create_bonus(username,bonusAmount=bonus,bonusPointAmount=point,ticketId_list=ticket_id_list,ticketQuantity=ticketQuantity,prmotion_id=promotion_id)
        
            claimid_list = backend.Search_Customer_bonus(username)
            logging.info(f"拿到 {len(claimid_list)} 筆 claimId")
            backend.Confirm_Customer_bonus(claimid_list)
                            
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
        
    try:
        frontend=Frontend(credential_fe)
        if frontend.token:
            Trans_id_list=frontend.get_Ticket_transaction_ID(merchantCode, username, ticket_id_list)
            frontend.approve_to_receive_ticket(Trans_id_list)
            # 領票後 extra_reward 未套用列表可能延遲寫入，略為等待再查 claim
            time.sleep(3)
            frontend.deposit_QAD(username, amount, Extra_Promo_ID)
            batch_approve(merchantCode)
            return True
            
        
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
            
            
            
    
    
    

   