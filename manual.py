import yaml,os
import requests,logging,json
from datetime import datetime
from openpyxl import Workbook
from itertools import cycle
from datetime import datetime,timedelta


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

    def create_bonus(self,player:str,prmotion_id:int):
        start_time =int((datetime.now()+timedelta(minutes=20)).timestamp()*1000)
        API_URL = "http://sit-admin2.tcg.com/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251" 
        params={
            "pid":20251
        }
        payload = {
        "merchantCode": "gi8viet",
        "promotionId": prmotion_id,
        "customerName": player,
        "playerRemark": "string",
        "bonusAmount": 10,
        "pointAmount": 10,
        "turnoverAmount": 10,
        "ticketId": 1313018,
        "ticketQuantity": 1,
        "isSendApp": "N",
        "appTitle": "",
        "appMessage": "恭喜您成功领取 {promotionName} 活动获得 金额 {bonus} 票卷 {ticket}",
        "scheduleTime": start_time
    }

        headers = self.header()
        cookies = self.cookie()
        try:
            response = requests.post(API_URL, params=params,json=payload, headers=headers, cookies=cookies, verify=False)
            response.raise_for_status()
            
            
            response_data = response.json()
            logging.info(f"狀態碼: {response.status_code}")
            logging.info(f"響應內容: {response_data}")
            
            
            if response_data.get("success"):
                return True
            else:
                response_data.get("message", "未知錯誤")
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
        
        current_dir=os.path.dirname(__file__)
        yaml_path=os.path.join(current_dir,"promotion_id.yaml")
        with open(yaml_path,"r",encoding="utf-8") as f:
            config=yaml.safe_load(f)
        prmotion_id_multiple=config.get("promotion_id",[])
        print(prmotion_id_multiple)
        account='top666'
        
        for promo  in prmotion_id_multiple:
            for _ in range(3):
                is_success=self.create_bonus(account,prmotion_id=promo)
                if is_success:
                    logging.info(f"創建手動紅利成功 活動ID{promo}")
                else:
                    logging.error(f"創建手動紅利失敗 活動ID{promo}")
              
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

    
    

   