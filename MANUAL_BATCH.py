import yaml
import os
import time
import requests
import logging
from datetime import datetime
from itertools import cycle
import threading
import concurrent.futures

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
token_lock = threading.Lock()
def create_bonus(clone_be_end, account, promo, bonusAmount, bonusPointAmount, ticket, ticketQuantity):
    result = {
        "player": account,
        "promo_id": promo,
        "bonusAmount": bonusAmount,
        "bonusPointAmount": bonusPointAmount,
        "ticket": ticket,
        "ticketQuantity": ticketQuantity,
        "create_result": "",
        "remark": "",
        "claimid": "",
        "confirm_result": "",
        "status": ""
    }
    is_success = clone_be_end.create_bonus(
        player=account,
        bonusAmount=bonusAmount,
        bonusPointAmount=bonusPointAmount,
        ticketId=ticket,
        ticketQuantity=ticketQuantity,
        prmotion_id=promo
    )

    if is_success:
        search_result = clone_be_end.Search_Customer_bonus()
        if search_result:
            for customerID, claimid,promotionType in search_result:
                if claimid:
                    result['claimid'] = claimid
                    time.sleep(0.5)
                    with clone_be_end.lock:
                        claim_dict={
                            "promoClaimId": claimid,
                            "promotionType": promotionType
                        }
                        if not any(item.get("promoClaimId")==claimid for item in clone_be_end.claimid_list):
                            clone_be_end.claimid_list.append(claim_dict)
                        else:
                            logging.info("一樣的claim_id跳過添加")

                
    else:
        logging.error("創建錯誤")

    return result

class B_end:
    @property
    def _headers(self):
        if not hasattr(self, '_cached_headers'):
            self._cached_headers={
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": self.token_data,
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
        return self._cached_headers
    
    def __init__(self,credential:dict):
        self.token=self.get_token(credential['operatorName'],credential['password'])
        self.credential=credential
        self.token_data=self.token
        self.claimid_list=[]
        self.success_count=0
        self.lock=threading.Lock()
        
    def get_token(self,operatorName,password):
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
            "platform": "",
            "Tac-Trace-Id":"&kZEwhHNN!Pe(Qj_"
        }
        
        cookies = {
            "language": "zh_CN",
            "JSESSIONID":"wK3EQfljeUHXxYAN8uKQcvkpKBg1WM4PaVshMx7TpsBoHDtAk4c_!-1653539373"
        }
        with token_lock:
            requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
            token_data=requests_data.json()
            token=token_data.get("token")
            logging.info(f"登入API回傳: {token}")
            return token

    def create_bonus(self,player:str,bonusAmount:int,bonusPointAmount:int,ticketId:int,ticketQuantity:int,prmotion_id:int):
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/mcs-manual-promotion-addManualPromotionClaim" 
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

        headers = self._headers
        cookies = {
            "language": "zh_CN"
        }
        try:
            response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
            response_data = response.json()
            
            if response_data.get("success") :
                logging.info(f"手動紅利發放成功, 玩家帳號{player} ")
                with self.lock:          
                    self.success_count += 1
                return True
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
    def Search_Customer_bonus(self):
      
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/get/mcs-manualPromotion-search" 
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        params = {
        "merchantCode": "gi8viet",
        "status": "P",
        "searchDateMode": "issuedDateSearch",
        "startTime": start_time,
        "endTime": end_time,
        "pageSize": 10,
        "pageNo": 1,
    }

        headers = self._headers
        
        try:
            result_list=[]
            response = requests.get(API_URL, params=params, headers=headers, verify=False)
            response.raise_for_status()
            
            response_data = response.json()
            
            if response_data.get("success") :
                customer_list=response_data.get("value",[])
                
                if not customer_list:
                    logging.error("回應中找不到 customerlist")
                for customer_info in customer_list:
                    CustomerID=customer_info.get("customerId")
                    claimid=customer_info.get("id")
                    promotionType=customer_info.get("promotionType")
                    promotionId=customer_info.get("promotionId")
                    logging.info(f"{claimid}和對應的{promotionType}和活動id{promotionId}")
                    if CustomerID and claimid:
                        result_list.append((CustomerID, claimid,promotionType))
                return result_list
            else:
                logging.error("回應中找不到 customerId 或 claimid")
                return []
            
                
        except requests.RequestException as e:
            logging.error(f"HTTP錯誤 {e}")
            return  []
        except ValueError as e:
            logging.error(f"JSON解析錯誤: {e}")
            return  []
        except Exception as e:
            logging.error(f"其他錯誤: {e}")
            return  []
    
    def Confirm_Customer_bonus(self):
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/mcs-manual-promotion-batchApproveRejectManualPromotion" 
        payload = {
            "status": "I",
            "promotionClaims": self.claimid_list
        }

        headers = self._headers
        try:
            response = requests.post(API_URL, json=payload, headers=headers, verify=False)
            response.raise_for_status()
            logging.info(self.claimid_list)
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
    
    def process_procedure(self):
        
        bonusAmount=10
        bonusPointAmount=10
        #count=2
        ticketQuantity=3
        current_dir=os.path.dirname(__file__)
        yaml_path=os.path.join(current_dir,"config.yaml")
        with open(yaml_path,"r",encoding="utf-8") as f:
            config=yaml.safe_load(f)
        prmotion_id_multiple=config.get("promtion_ids",[])
        ticket_id=config.get("ticket_id")
        testing_account=config.get("testing_account")
        create_record=[]
        ticket_cycle=cycle(ticket_id)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_tasks=[]
            for account in testing_account:
                for promo in prmotion_id_multiple:
                    ticket = next(ticket_cycle) 
                    future=executor.submit(
                            create_bonus,  
                            self,      
                            account,
                            promo,
                            bonusAmount,
                            bonusPointAmount,
                            ticket,
                            ticketQuantity,
                    )
                    future_tasks.append(future)
            for future in concurrent.futures.as_completed(future_tasks):
                result=future.result()
                create_record.append(result)  
        logging.info(f"總共處理 {len(create_record)} 筆，成功 {self.success_count} 筆")
        time.sleep(2)

        is_confirm_complete=self.Confirm_Customer_bonus()
        if is_confirm_complete:
            return True
        else:
            return False
        
    
def main():

    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        
        b_end=B_end(credential)
        if b_end.token:
            if b_end.process_procedure():
                return True
            else:
                return False
        else:
            logging.error("登入失敗 無法取得Token")
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")



   