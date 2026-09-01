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
        
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251" 
        payload = {
        "merchantCode": "gi8viet",
        "customerName": player,
        "bonusAmount": bonusAmount,
        "pointAmount": bonusPointAmount,
        "turnoverAmount": 0,
        "promotionId": prmotion_id,
        "toReqAmount": 0,
        "ticketId": ticketId,
        "ticketQuantity": ticketQuantity,
        "isSendApp": "N"
    }

        headers = self.header()
        cookies = self.cookie()
        try:
            response = requests.post(API_URL, json=payload, headers=headers, cookies=cookies, verify=False)
            response.raise_for_status()
            
            
            response_data = response.json()
            logging.info(f"狀態碼: {response.status_code}")
            logging.info(f"響應內容: {response_data}")
            return True
            
        
        except AssertionError:
            raise        
        except requests.RequestException as e:
            logging.error(f"HTTP錯誤 {e}")
            return False
        except ValueError as e:
            logging.error(f"JSON解析錯誤: {e}")
            return False
        except Exception as e:
            logging.error(f"其他錯誤: {e}")
            return False
    def Search_Customer_bonus(self,token,player:str,merchant:str):
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/get/prom-promotion-manual-reward-claims" 
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        params = {
        "merchantCode": merchant,
        "status": "P",
        "customerName":player,
        "relayDisableEncode": True,
        "isForProcessingAll": False,
        "periodType": "ISSUE_PERIOD",
        "startTime": start_time,
        "endTime": end_time,
        "pageSize": 10,
        "pageNo": 1,
        "pid" :20250
        }

        headers = self.header(token,merchant)
        cookie={
            "Cookie": "language=zh_CN"
        }
        try:
            response = requests.get(API_URL, params=params, headers=headers, cookies=cookie, verify=False)
            response.raise_for_status()
            
            response_data = response.json()
            
            if response_data.get("success"):
                logging.info(f"完整回應: {json.dumps(response_data, ensure_ascii=False)}")
                
                customer_list=response_data.get("value",[])
                value = response_data.get("value", {})
                customer_list = value.get("list", [])
                if customer_list:
                    customer_info=customer_list[0]
                    CustomerID=customer_info.get("customerId")
                    claimid=customer_info.get("claimId")
                    promoType=customer_info.get("promotionType")
        
                    if CustomerID and claimid:
                        logging.info(f"拿到 CustomerID: {CustomerID} 和 claimid: {claimid} {promoType}")
                        return CustomerID, claimid,promoType
                # FIX: customer_list 為空時補上 return
                logging.error("customer_list 為空，找不到待審核記錄")
                return None, None, None
            else:
                logging.error(response_data)
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
            
            assert response_data.get("success"), f"審核失敗{response_data.get('message')}"
            return True
        
        except AssertionError:
            raise
        except requests.RequestException as e:
            logging.error(f"HTTP錯誤 {e}")
            return False
        except ValueError as e:
            logging.error(f"JSON解析錯誤: {e}")
            return False
        except Exception as e:
            logging.error(f"其他錯誤: {e}")
            return False

    create_record=[]
    def process_procedure(self):
        bonusAmount=10
        bonusPointAmount=0
        #count=2
        ticketQuantity=3
        current_dir=os.path.dirname(__file__)
        yaml_path=os.path.join(current_dir,"config.yaml")
        with open(yaml_path,"r",encoding="utf-8") as f:
            config=yaml.safe_load(f)
        prmotion_id_multiple=config.get("promotion_id",[])
        ticket_id=config.get("ticket_id_gi8viet")
        testing_account=config.get("testing_account1")
        ticket_id_cycle=cycle(ticket_id)
        try:
            for account in testing_account:
                for promo  in prmotion_id_multiple:
                    ticket=next(ticket_id_cycle)
                    print(account)
                    is_success=self.create_bonus(account,bonusAmount=bonusAmount,bonusPointAmount=bonusPointAmount,ticketId=ticket,ticketQuantity=ticketQuantity,prmotion_id=promo)
                    if is_success:
                        logging.info("creating bonus success")
                        '''
                        Customerid,self.claimid = self.Search_Customer_bonus(account)
                        if self.claimid :
                            self.claimid_list.append(self.claimid)
                        if Customerid  and self.claimid :
                            self.Confirm_Customer_bonus(Customerid)
                            '''
                    else:
                        logging.error("creating bonus failed")
        except Exception as e:
            logging.error(f"處理過程中發生錯誤: {e}")
                
            
def main():
    print("收到 submit 請求")
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        b_end=B_end(credential)
        if b_end.token:
            b_end.process_procedure()
        else:
            logging.error("登入失敗 無法取得Token")
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
        
main()

    
    

   