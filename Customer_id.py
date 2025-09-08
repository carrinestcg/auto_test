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
    def header(self):
        return{
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_data,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/311792",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG"
        }
    def header_rank(self,username):
        return{
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_data,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": f"http://sit-admin2.tcg.com/20106/{username}-gi8viet",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG"
        }
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
        headers ={"Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "",
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/311792",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG"
        }
        cookies = {
            "language": "zh_CN"
        }
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token
    def search_customerid(self,player:str):
        
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/player-search-non-bankcard?merchantCode=gi8viet&isWildcard=false&sortType=desc&pageable=true&data={player}&searchCode=USERNAME"  
        
        headers=self.header()
        cookies = {
            "language": "zh_CN"
        }
        try:
            response=requests.get(API_URL2, headers=headers, cookies=cookies, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") == True:
                value_data=response_data.get('value',{})
                player_list=value_data.get('list',[])
                if player_list:
                    customerId=player_list[0].get("customerId")
                    if customerId:
                        logging.info(f"拿到玩家資訊: {player}")
                        logging.info(f"CustomerID: {customerId}")
                    else:
                        logging.error("沒有拿到CustomerID")
                    return customerId
                else:
                    logging.error("沒有拿到List")
                
            else:
                error_msg = response_data.get("message", "未知錯誤")
                logging.error(f"未拿到玩家資訊: {error_msg}")
                return False
        except Exception as e:
            logging.error(f"狀態碼: {response.status_code}")
    def search_customer_rank(self,customer_id:int,username):
        
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-player-basic-information-getHeaderInfo"  
        
        headers=self.header_rank(username)
        cookies = {
            "language": "zh_CN"
        }
        params={
            "customerId":customer_id,
            "merchantCode":"gi8viet"
        }
        try:
            response=requests.get(API_URL2, headers=headers, cookies=cookies,params=params, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") == True:
                value_data=response_data.get('value',{})
                player_rank=value_data.get("memberLabel")
                if player_rank:
                    logging.info(f"玩家等級: {player_rank}")
                    return player_rank
                else:
                    logging.error("沒有拿到玩家等級")
                    return None
            else:
                error_msg = response_data.get("message", "未知錯誤")
                logging.error(f"未拿到玩家資訊: {error_msg}")
                return False
        except Exception as e:
            logging.error(f"狀態碼: {response.status_code}")
    def get_register_time(self,customer_id):
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-player-basic-information-getPlayerDetail"  
        headers= headers=self.header_rank(customer_id)
        params={
                    "merchantCode":"gi8viet",
                    "customerId": customer_id

        }
        cookies = {
                    "language": "zh_CN",
                }
        try:
            response=requests.get(API_URL2,headers=headers,params=params,cookies=cookies,verify=False)
            response_data=response.json()
            if response_data.get("success")==True:
                value_list=response_data.get("value",{})
                register_time=value_list.get("registerTime")
                if register_time:
                    register_time_str=datetime.fromtimestamp(register_time/1000).strftime("%Y-%m-%d %H:%M:%S")
                    logging.info(f"register_time_str: {register_time_str}")
                return register_time_str
            else:
                logging.error(f"API Response: {response.text}")

        except Exception as e:
                logging.error(f"{e}")

      
    def get_deposit_counts(self,regester_date,player):
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/post/ods-v2-user-member-psersonal-info"  
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        headers=self.header_rank(player)
        params={
                    "customerName":player,
                    "regStartDate":regester_date,
                    "regEndDate":end_time,
                    "page":1,
                    "size":10,
                    "subordinateType":"SELF",
                    "pageable":True,
                    "pagedExport":False,
                    "needTotalCount":False,
                    "needTotalCount":False,
                    "privilege":False,
                    "merchantCode":"gi8viet",
                    "withdrawerNamePrivilege":False

        }
        payload={
                    "customerName":player,
                    "regStartDate":regester_date,
                    "regEndDate":end_time,
                    "page":1,
                    "size":10,
                    "subordinateType":"SELF",
                    "pageable":True,
                    "pagedExport":False,
                    "needTotalCount":False,
                    "needTotalCount":False,
                    "privilege":False,
                    "withdrawerNamePrivilege":False

        }
        cookies = {
                    "language": "zh_CN",
                }
        try:
            response=requests.post(API_URL2,headers=headers,params=params,json=payload,cookies=cookies,verify=False)
            response_data=response.json()
            if response_data.get("success")==True:
                value_list=response_data.get("value",{})
                deposit_count_list=value_list.get("list", [])
                if deposit_count_list:
                    deposit_count=deposit_count_list[0].get("depositCounts")
                    logging.info(f"取得存款次數: {deposit_count}")
                    return deposit_count
                else:
                    logging.error(f"沒有拿到list")
            else:
                logging.error(f"API Response: {response.text}")

        except Exception as e:
                logging.error(f"{e}")        
def main(username):
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    backend=B_end(credential)
    if backend.token:
        customer_id=backend.search_customerid(username)
        customer_rank=backend.search_customer_rank(customer_id,username)
        register_time=backend.get_register_time(customer_id)
        deposit_count=backend.get_deposit_counts(register_time,username)
        return customer_id,customer_rank,deposit_count