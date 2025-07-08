import requests,logging,datetime
from datetime import datetime,timedelta
import time,random,yaml,os
from openpyxl import Workbook
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
        self.record_data_list=''
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
            "platform": ""
        }
        
        cookies = {
            "language": "zh_CN"
        }
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token

    def Bonus_record_page(self):
        
        current_dir=os.path.dirname(__file__)
        yaml_path=os.path.join(current_dir,"config.yaml")
        with open(yaml_path,"r",encoding="utf-8") as f:
            config=yaml.safe_load(f)
        VIP_testing_account_list=config.get("VIP_testing_account")
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/promo-promotion-rank_salary-claim_report"  
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
            "Tac-Trace-Id":"o0R%xv5@AKx^&6lQ",
            "Referer": "http://sit-admin2.tcg.com/20324",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG"
        }
        params={
            "status":"A",
            "periodType":"CLAIM_PERIOD",
            "startTime":start_time,
            "endTime":end_time,
            "page":1,
            "size":1

        }
        cookies = {
            "language": "zh_CN",
        }
        try:
            response=requests.get(API_URL2, headers=headers, params=params, cookies=cookies, verify=False)

            response_data=response.json()
            if response_data.get("success") == True:
                self.record_data_list=response_data.get('value',{})
                for account in self.record_data_list:
                    if account in VIP_testing_account_list:
                        logging.info("有正確存在於派發紀錄")
                        return True
                    else:
                        logging.info("沒有正確存在於派發紀錄")
                        return False
            else:
                response_data.get("message", "未知錯誤")
                return False
            
        except Exception as e:
            logging.error(f"狀態碼: {response.status_code}")
        
if __name__ == "__main__":
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        b_end=B_end(credential)
        if b_end.token:
            b_end.Bonus_record_page()
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)

    #填入玩家帳號
    
    
    

   