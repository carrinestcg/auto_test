import requests,logging,datetime
from datetime import datetime
import yaml,os,sys


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Backend:
    def __init__(self,credentail:dict):
        self.credential=credentail
        self.session=requests.Session()
        self.token=self.get_token()
    def header(self,MerchantCode):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": str(MerchantCode),
            "MerchantCode": str(MerchantCode),
            "Referer": "http://sit-admin2.tcg.com/24782",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "notPending": "true",
            "platform": "TCG"
        }
    def cookie(self):
        return {
            "language": "zh_CN"
        }
        
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
        
        cookies = self.cookie()
        requests_data=self.session.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        self.token=token_data.get("token")
        return self.token


    def search_depositid(self,MerchantCode:str):
        
        API_URL2="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-depositPromotion-searchDepositPromotionList"  
        
        param={
            "status":"A",
            "merchantCode":"gi8viet",
            "pageSize":1000,
            "pageNo":1
        }
        headers=self.header(MerchantCode)
        cookies = self.cookie()
        try:
            response=self.session.get(API_URL2, headers=headers, cookies=cookies, params=param,verify=False)
            response.raise_for_status()
            id_list=[]
            response_data=response.json()
            if response_data.get("success") :
                value_list=response_data.get("value",[])
                if value_list:
                    for deposit in value_list:
                        deposit_id=deposit.get("id")
                        if deposit_id:
                            id_list.append(deposit_id)
                        else:
                            logging.error("沒有拿到id")
                            return None
                    return id_list
                else:
                    logging.error("沒有拿到list")
            
            else:
                error_msg = response_data.get("message", "未知錯誤")
                logging.error(f"未拿到玩家資訊: {error_msg}")
                return False
        except Exception as e:
            logging.error(f"狀態碼: {response.status_code}")

    def turn_off_deposit_promotion(self,MerchantCode:str,id_list:list):
        for id in id_list:
            url="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-depositPromotion-editStatus"
            headers=self.header(MerchantCode)
            params={
                "merchantCode":MerchantCode,
                "id":id,
                "status":"I"
            }
            cookies = self.cookie()
            payload={}
            response=self.session.post(url, headers=headers, cookies=cookies, params=params,json=payload,verify=False)
            response_data=response.json()
            if response_data.get("success") :
                logging.info("更新狀態成功")
                logging.info(f"關閉promotion_id{id}")
                
            else:
                error_msg = response_data.get("message", "未知錯誤")
                logging.error(f"更新狀態失敗: {error_msg}")
                return False
            
    def procedure(self,merchantCode):
        try:
            
            id_list=self.search_depositid(merchantCode)
            if not id_list:
                logging.error("沒有拿到id_list")
            self.turn_off_deposit_promotion(merchantCode,id_list)
            

        except Exception as e:
            logging.error(e)
        except KeyboardInterrupt:
            print("退出程式")
            sys.exit()

def main_batch(merchantCode):
        credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
        }
        try:
            b_end=Backend(credential)
            if b_end.token:
                b_end.procedure(merchantCode)
                

        except Exception as e:
            logging.error(e)
merchantCode="gi8viet"
main_batch(merchantCode)

            
        

   