import yaml,os
import requests
import logging
import json
from datetime import datetime,timedelta
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
    def header(token,merchant):
        return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": token,
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Language": "zh_CN",
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/24785",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "TCG3",
        "Merchant": merchant,
        "merchantCode": merchant,
        "platform": "TCG"
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
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token

    def batch_validate(self,ticketId:int, merchantCode:str, prmotion_id:int):
        
        for prmotion_id in prmotion_id_multiple:
            
            API_URL = "http://10.81.1.88:8083/promo-be/resources/promotion/manual_reward/claims/batch/validate" 
            params = {
            "merchantCode": merchantCode,
            "promotionId": prmotion_id,
            "ticketId": ticketId,
            "isTrimFirst": True,
            "isAuto": True,
        }

            headers = self.header(merchantCode)
            file_path="ManualPromotion (2) (1).xlsx"
            files = {
                "imageFile": (file_path, open(file_path, "rb"), "/Users/user/Downloads/ManualPromotion (2) (1).xlsx")
            }
            cookies = {
                "language": "zh_CN"
            }
            try:
                response = requests.post(API_URL, params==params, headers=headers, cookies=cookies,files=files, verify=False)
                response.raise_for_status()
                
                
                response_data = response.json()
                logging.info(f"狀態碼: {response.status_code}")
                logging.info(f"響應內容: {response_data}")
                
                
                if response_data.get("success") :
                    value=response_data.get("value",{})
                    taskId=value.get("taskId")
                    logging.info(f"驗證成功 取得任務ID: {taskId}")
                    return taskId
                else:
                    error_msg = response_data.get("message", "未知錯誤")
                    logging.error(f"上傳驗證失敗: {error_msg}")
                    return None
                    
            except requests.RequestException as e:
                logging.error(f"HTTP錯誤 {e}")
                return False
            except ValueError as e:
                logging.error(f"JSON解析錯誤: {e}")
                return False
            except Exception as e:
                logging.error(f"其他錯誤: {e}")
                return False
    def batch_auto_approve(self,ticketId:int, merchantCode:str, prmotion_id:int, task_id:str):
        
        for prmotion_id in prmotion_id_multiple:
            
            API_URL = "http://10.81.1.88:8083/promo-be/resources/promotion/manual_reward/claims/batch/auto_approve" 
            params = {
            "merchantCode": merchantCode,
            
              }
            payload={
                "taskId": task_id,
                "promotionId": prmotion_id,
                "ticketId": ticketId,
                "isApplyVendorLockAll": True,
                "isSendApp": "Y",
                "appTitle": "title",
                "appMessage": "恭喜您成功领取 {promotionName} 活动获得 金额 {bonus} 票卷 {ticket}",
                "allowMail": "Y",
                "emailTO": {
                    "emailProviderId": 0,
                    "title": "string",
                    "content": "string"
                }
                }
            headers = self.header(merchantCode)
            
            cookies = {
                "language": "zh_CN"
            }
            try:
                response = requests.post(API_URL, params==params, headers=headers, cookies=cookies, json=payload, verify=False)
                response.raise_for_status()
                
                
                response_data = response.json()
                logging.info(f"狀態碼: {response.status_code}")
                logging.info(f"響應內容: {response_data}")
                
                
                if response_data.get("success") :
                    logging.info("上傳驗證成功 ")
                    return True
                else:
                    error_msg = response_data.get("message", "未知錯誤")
                    logging.error(f"上傳驗證失敗: {error_msg}")
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
        
    
if __name__ == "__main__":

    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        b_end=B_end(credential)
        if b_end.token:
            current_dir=os.path.dirname(__file__)
            yaml_path=os.path.join(current_dir,"promotion_id.yaml")
            with open(yaml_path,"r",encoding="utf-8") as f:
                config=yaml.safe_load(f)
            prmotion_id_multiple=config.get("promotion_ids",[])
            ticket_id_cycle=cycle(config.get("ticket_ids", []))
            merchantCode='gi8viet'
            for prmotion_id in prmotion_id_multiple:
                ticketId=next(ticket_id_cycle)
                task_id = b_end.batch_validate(ticketId, merchantCode, prmotion_id)
                b_end.batch_auto_approve(ticketId, merchantCode, prmotion_id, task_id)
        else:
            logging.error("登入失敗 無法取得Token")
    except Exception as e:
        logging.error(f"啟動時發生錯誤: {e}")
    
    

   