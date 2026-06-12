import requests
import logging
import urllib3
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Delete_achievement:
    def __init__(self,credential:dict):
        self.credential=credential
        self.token=self.get_token()
    def get_token(self):
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
                "Merchant": 'gi8viet',
                "MerchantCode": 'gi8viet',
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

    def batch_delete_new_register_(self, promotionId_list:list):
        for promotionId in promotionId_list:
            print(promotionId)
            URL="http://sit-admin2.tcg.com/tac/api/relay/put/prom-promotion-promo-code-status"
            header={
                "accept":"*/*",
                "Accept-Encoding":"gzip, deflate, br",
                "merchantCode": "gi8viet",
                "operatorName": "carrine03",
                "Authorization": self.token
            }
            params={
                    "merchantCode":"gi8viet",
                    "promotionSettingId":promotionId,
                    "status": "I",
                    "pid": 26009
                }
            
            
            respone=requests.put(URL,headers=header, params=params,verify=False)
            respone_json=respone.json()
            if respone.status_code==200:
                
                logging.info("成功")
                
            else:
                logging.info(f"失敗 原因:{respone_json}")
                
    def get_new_register_list(self):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/prom-promotion-promo-code-list"
        header={
            "accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "merchantCode": "gi8viet",
            "Authorization": self.token,
            "environment": "TCG3",       
            "platform": "TCG",          
            "language": "zh_CN",         
            "customTimezone": "Etc/GMT-8"
        }
        params={
            "status":"A",
            "merchantCode":"gi8viet",
            "pageSize":1000,
            "pageNo":1,
            "pid":26001,
        }
        promotionId_list=[]
        respone=requests.get(URL,headers=header, params=params, verify=False)
        respone_json=respone.json()
        if respone_json.get("success"):
            value=respone_json.get("value", {})
            value_list=value.get("list", [])
            for item in value_list:
                promo_id=item.get("promotionSettingId")
                
                if promo_id:
                    logging.info("拿到promo_id和 名稱")
                    promotionId_list.append(promo_id)
                else:
                    logging.error("沒有拿到資訊")
            return promotionId_list
        else:
            logging.error("查詢失敗")
    
def main():

    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
        }
    try:
        b_end = Delete_achievement(credential)
        if b_end.token:
            promotionId_list = b_end.get_new_register_list()
            logging.info(f"取得 {len(promotionId_list)} 筆資料: {promotionId_list}")  # 先確認有沒有拿到
            if promotionId_list:
                b_end.batch_delete_new_register_(promotionId_list)
            else:
                logging.warning("沒有找到任何資料")
    except Exception as e:
        logging.error(e)
        
main()