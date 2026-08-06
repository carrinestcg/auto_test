import requests
import logging
from datetime import datetime
import yaml
import os
import sys
import deposit_api

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Backend:
    def __init__(self,credentail:dict):
        self.credential=credentail
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
        self.token=token_data.get("token")
        return self.token


    def Deposit_API(self,player:str,MerchantCode:str,deposit_amount:int):
        
        API_URL2="http://sit-admin2.tcg.com/mcs_console/api/deposit/createDeposit"  
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": str(MerchantCode),
            "MerchantCode": str(MerchantCode),
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/20000",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "notPending": "true",
            "platform": "TCG"
        }
        payload={
            "merchantCode": MerchantCode,
            "username": player,
            "depositType": 52,
            "bankAcctId": 32267,
            "requestDateString":start_time,
            "requestAmount": deposit_amount,
            "customerBankCharge": 0,
            "bankCharge": ""
        }
        cookies = {
            "language": "zh_CN"
        }
        try:
            response=requests.post(API_URL2, headers=headers, cookies=cookies, json=payload,verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success"):
                logging.info("充值成功")
            else:
                logging.error("充值失敗")
           
                
        except Exception as e:
            logging.error(f"狀態碼: {response.status_code},{e}")


    def procedure(self,username_list, merchantCode, amount):
        success_count = 0
        count = len(username_list)
        try:
            print(username_list, merchantCode, amount)
            for username in username_list:
                self.Deposit_API(username,merchantCode,amount)
                success_count += 1
            if success_count == count:
                logging.info(f"所有 {count} 個用戶充值成功")
                deposit_api.batch_approve(merchantCode)
                return True
            else:
                logging.error(f"成功充值 {success_count} 個用戶，失敗 {count - success_count} 個用戶")
                return False

        except Exception as e:
            logging.error(e)
        except KeyboardInterrupt:
            print("退出程式")
            sys.exit()

def main_batch(username_list, merchantCode, amount):
       
        credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
        }
        try:
            b_end=Backend(credential)
            if b_end.token:
                result = b_end.procedure(username_list, merchantCode, amount)
            return result

        except Exception as e:
            logging.error(e)
        

   