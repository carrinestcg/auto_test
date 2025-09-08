import yaml,os
import requests,logging,json
from datetime import datetime
from openpyxl import Workbook
from itertools import cycle


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class B_end:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.password=''
        self.token=self.get_token(credential['operatorName'],credential['password'])
        self.credential=credential
        self.token_data=self.token
        self.record_data_list=[]
        self.claimid_list=[]
        self.success_count=0
        self.claimid=''
    def header(self):
        return{
        
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
    def cookie(self):
        return {
            "language": "zh_CN"
        }
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
        cookies = self.cookie()

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

        headers = self.header()
        cookies = self.cookie()
        try:
            response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
            response.raise_for_status()
            
            
            response_data = response.json()
            logging.info(f"狀態碼: {response.status_code}")
            logging.info(f"響應內容: {response_data}")
            
            
            if response_data.get("success") == True:
                logging.info(f"手動紅利發放成功 ")
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

        headers = self.header()
        cookies = self.cookie()
        try:
            response = requests.get(API_URL, params=payload, headers=headers, cookies=cookies, verify=False)
            response.raise_for_status()
            
            response_data = response.json()
            
            
            if response_data.get("success") == True:
                customer_list=response_data.get("value",[])
                
                if not customer_list:
                    logging.error("回應中找不到 customerlist")

                customer_info=customer_list[0]
                CustomerID=customer_info.get("customerId")
                claimid=customer_info.get("id")
        
                if CustomerID and claimid:
                    return CustomerID, claimid
                
            else:
                    logging.error("回應中找不到 customerId 或 claimid")
                    return None, None 
            
                
        except requests.RequestException as e:
            logging.error(f"HTTP錯誤 {e}")
            return None, None
        except ValueError as e:
            logging.error(f"JSON解析錯誤: {e}")
            return None, None
        except Exception as e:
            logging.error(f"其他錯誤: {e}")
            return None, None
    
    def Confirm_Customer_bonus(self,Customerid:int):
    
        API_URL = f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-manual-promotion-approveClaimStatus?claimStatus=I&customerId={Customerid}&claimId={self.claimid}" 
        payload = {
        "internalRemark": ""
        }

        headers = self.header()
        cookies = self.cookie()
        try:
            response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
            response_data = response.json()
            
            if response_data.get("success") == True:
                logging.info(f"審核活動紅利成功 ")
                return True
            else:
                error_msg = response_data.get("value" )
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
    def Bonus_record_page(self):
        
      
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-v2-promotionClaim-search?pageSize=20&pageNo=1"  
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_data,
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
        cookies = self.cookie()
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
    def process_procedure(self,player_acount,promo):
        
        bonusAmount=10000
        bonusPointAmount=0
        #count=2
        ticketQuantity=3
        current_dir=os.path.dirname(__file__)
        yaml_path=os.path.join(current_dir,"config.yaml")
        with open(yaml_path,"r",encoding="utf-8") as f:
            config=yaml.safe_load(f)
        ticket_id=config.get("ticket_id")
        
        for ticket in ticket_id:
            is_success=self.create_bonus(player_acount,bonusAmount=bonusAmount,bonusPointAmount=bonusPointAmount,ticketId=ticket,ticketQuantity=ticketQuantity,prmotion_id=promo)
            if is_success:
                Customerid,self.claimid = self.Search_Customer_bonus(player_acount)
                if Customerid  and self.claimid :
                    self.Confirm_Customer_bonus(Customerid)
                else:
                    logging.error("審核失敗")
        
    
def main(player_account,promo):
    print("收到 submit 請求")
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        b_end=B_end(credential)
        if b_end.token:
            b_end.process_procedure(player_account,promo)
        else:
            logging.error("登入失敗 無法取得Token")
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
    
    

   