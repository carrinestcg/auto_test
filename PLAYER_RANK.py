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
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/24785",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "TCG3",
        "merchantCode": "gi8viet",
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
    def cookie(self):
        return{
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
    def search_customerid(self,player:str):
        
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/player-search-non-bankcard?merchantCode=gi8viet&isWildcard=false&sortType=desc&pageable=true&data={player}&searchCode=USERNAME"  
        
        headers=self.header()
        cookies = self.cookie()
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
    def player_rank(self,customerId:int,player:str,Level:int):
    
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-changePlayerLabel-VIP-level?customerId={customerId}&newLabelId={Level}&oldLabelId=62537&remark=x"
        
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_data,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": f"http://sit-admin2.tcg.com/20106/{player}-gi8viet",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG",
        }
        cookies = self.cookie()
        try:
            response=requests.post(API_URL3, cookies=cookies, headers=headers, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") == True:
                logging.info("更新等級成功")
                return True  
            else:
                logging.error("沒有拿到value")
                return False
        
        except Exception as e:
            logging.error(f"更新等級失敗{e}")

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
        cookies = {
            "language": "zh_CN",
            "JSESSIONID":"wK3EQfljeUHXxYAN8uKQcvkpKBg1WM4PaVshMx7TpsBoHDtAk4c_!-1653539373"
        }
        try:
            response=requests.get(API_URL2, headers=headers, params=payload, cookies=cookies, verify=False)

            response_data=response.json()
            if response_data.get("success") == True:
                self.record_data_list=response_data.get('value',{})
                return True
            else:
                response_data.get("message", "未知錯誤")
                return False
            
        except Exception as e:
            logging.error(f"狀態碼: {response.status_code}")
    def process_procedure(self,username):
        L1=62785
        L2=62786
        L3=62787
        L4=62788
        L5=62789
        L6=62790
        L7=62816
        random_level=random.choice([L1,L2,L3,L4,L5,L6,L7])
        wb=Workbook()
        ws=wb.active
        ws.title="紅利發放結果"
        ws.append(["玩家帳號","活動名稱","玩家等級","活動類型", "紅利金額", "積分", "票卷", "票卷張數", "更新等級結果", "紅利派發紀錄"])
        bonusAmount=1000
        bonusPointAmount=30
        #count=2
        random_ticket=random.choice([1004007,1004006,1004008,1004010,1004009,1010009])
        ticketQuantity=3
        #ticket=1105015
        update_result='尚未更新等級'
        bonus_record=''
        playerRemark=''
        if self.Bonus_record_page():
            first_record=self.record_data_list[0]
            promotion_name=first_record.get("promotionName")
            type=first_record.get("type")
            playerRemark=first_record.get("labelName")
            ws.append([
                    username,
                    promotion_name,
                    playerRemark,
                    type,
                    bonusAmount,
                    bonusPointAmount,
                    random_ticket,
                    ticketQuantity,
                    update_result,
                    bonus_record
                    ]
                )
        logging.info("先寫入還沒有手動升級前的紅利派發紀錄")
        Customerid= self.search_customerid(username)
        if Customerid :
            player_rank_update_complete=self.player_rank(Customerid,username,random_level)
            if player_rank_update_complete:
                update_result='更新等級成功'
            else:
                update_result='更新等級失敗'
        if self.Bonus_record_page():
            logging.info("獲取紅利派發紀錄")
            first_record=self.record_data_list[0]
            promotion_name=first_record.get("promotionName")
            type=first_record.get("type")
            playerRemark=first_record.get("labelName")
            bonus_record='紅利派發紀錄更新'      
            ws.append([
                    username,
                    promotion_name,
                    playerRemark,
                    type,
                    bonusAmount,
                    bonusPointAmount,
                    random_ticket,
                    ticketQuantity,
                    update_result,
                    bonus_record
                    ]
                )
        else:
            logging.error("無法獲取紅利記錄")
        report_path=os.path.join(f"bonus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        wb.save(report_path)        
        
def main(username):
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        b_end=B_end(credential)
        if b_end.token:
            b_end.process_procedure(username)
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)

    #填入玩家帳號
    
    
    

   