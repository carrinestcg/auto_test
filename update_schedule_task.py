import requests
import logging
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class close_schedule_task:
    def __init__(self,credential:dict):
        self.credential=credential
        self.token=self.get_token(self.credential.get("merchantCode"))
    def get_token(self, merchatCode):
            login_url="http://sit-admin2.tcg.com/tac/api/login/password"
            payload={
                "operatorName": "carrine03",
                "password": "Test@1234"
            }
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": "",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Merchant": merchatCode,
                "MerchantCode": merchatCode,
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
            logging.info(f"狀態碼{requests_data.status_code}")
            requests_data.raise_for_status()
            token_data=requests_data.json()
            return token_data.get("token")

    def get_close_schedule_task(self, merchatCode:str):
        setting_list=[]
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/promo-promotion-schedule-task-list"
        header={
            "accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "merchantCode": merchatCode,
            "operatorName": "carrine03",
            "Authorization": self.token
        }
        
        params={
            "pid":203511,
            "page": 1,
            "size":1000,
            "sortOrder":"desc",
            "status":"A"
        }
        
        respone=requests.get(URL,headers=header, params=params,verify=False)
        respone_json=respone.json()
        if respone.status_code==200:
            print (respone_json)
            values=respone_json.get("values", [])
            for item in values: 
                settingId=item.get("settingId")
                setting_list.append(settingId)
                logging.info("拿取資料成功")

            return setting_list
            
        else:
            logging.info(f"失敗 原因:{respone_json}")
            return None
                
    def batch_close_schedule_task(self, setting_list:list, merchatCode:str):
        for settingId in setting_list:
            URL="http://sit-admin2.tcg.com/tac/api/relay/put/promo-promotion-schedule-task-update-status?pid=203511"
            header={
                "accept":"*/*",
                "Accept-Encoding":"gzip, deflate, br",
                "merchantCode": merchatCode,
                "Authorization": self.token,
                "environment": "TCG3",       
                "platform": "TCG",          
                "language": "zh_CN",         
                "customTimezone": "Etc/GMT-8"
            }
            payload={
                    "settingId": settingId,
                    "status": "I"
                }
        
            respone=requests.put(URL,headers=header, json=payload, verify=False)
            respone_json=respone.json()
            if respone_json.get("success"):
                time.sleep(1)
                logging.info("更新成功")
                    
                
            else:
                logging.error("更新失敗")
        return True
            
def main(merchatCode):

    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
        }
    try:
        b_end = close_schedule_task(credential)
        if b_end.token:
            settingId_list = b_end.get_close_schedule_task(merchatCode)
            logging.info(f"取得 {len(settingId_list)} 筆資料: {settingId_list}")  # 先確認有沒有拿到
            if settingId_list:
                result=b_end.batch_close_schedule_task(settingId_list, merchatCode)
                if result:
                    logging.info("批次更新成功")
                    return True
            else:
                logging.warning("沒有找到任何資料")
                return False
    except Exception as e:
        logging.error(e)

        
