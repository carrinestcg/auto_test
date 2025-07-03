import requests,logging,time
from datetime import datetime,timedelta
from openpyxl import Workbook
import random,os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def __init__(self,credential_fe:dict,credential_be:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential_fe=credential_fe
        self.credential_be=credential_be
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login_frontend(credential_fe['username'],credential_fe['password'])
        self.PromoCode_list=''
        self.promoID=''
        self.i=0
        self.token_backend=self.get_token_backend(credential_be['operatorName'],credential_be['password'])
        self.record_data_list=''
    def get_token_backend(self,operatorName,password):
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
    def get_token_login_frontend(self, username, password):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url='http://www.sit-gi8viet.com/wps/session/login/unsecure'
            
            headers = {
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                
            }
            login_data={
                'username':username,
                'password':password
            } 
            self.username=username
            requests_data=self.session.post(login_url,json=login_data,headers=headers)
            print(requests_data.text)
            self.username = requests_data.json()['value']['userName']
            self.userid = requests_data.json()['value']['id']
            self.token=requests_data.json()['value']['token']

            self.token_expire=datetime.now()+timedelta(minutes=25)
            return self.token
        
        except requests.RequestException as e:
            logging.error(f"請求失敗{e}")
            return None
    def is_token_valid(self):
        
        return (self.token is not None and 
                self.token_expire is not None and 
                datetime.now() < self.token_expire)
    
    def get_promo_code_list(self):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL=f"http://www.sit-gi8viet.com/wps/relay/PROMOFE_getPromoCode?_={unit_time}"
        headers={
            'Content-Type': 'application/json',
            'X-Timestamp':unit_time,
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'EN',
            'Merchant': 'gi8viet',
            'Origin': 'http://www.sit-gi8viet.com',
            'Referer': 'http://www.sit-gi8viet.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        response = self.session.get(login_URL, headers=headers, verify=False)
        response_json=response.json()

        if response_json.get('success')==True:
            self.PromoCode_list=response_json.get("value",[])
            
        else:
            logging.error(f"沒拿到優惠碼ID")
            return 
    def click_promo_code(self,promoCode):
        if not self.is_token_valid():
            logging.info("token 過期, 重新登入")
            self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
        if self.token is None:
            return
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        login_URL="http://www.sit-gi8viet.com/wps/relay/PROMOFE_claimPromoCode"
        headers={
            'Content-Type': 'application/json',
            'X-Timestamp':unit_time,
            "Authorization":self.token,
            'Connection': 'keep-alive',
            'Language': 'EN',
            'Merchant': 'gi8viet',
            'Origin': 'http://www.sit-gi8viet.com',
            'Referer': 'http://www.sit-gi8viet.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        payload={
             "promoCode": promoCode
        }
        
        cookies = {
            '_ga': 'GA1.1.343769134.1743155195',
            'SHELL_deviceId': '9248aea2-32ed-4b1a-afa9-d039ed6d1b95',
            '_ga_ABCD123456789': 'GS1.1.1743388368.2.1.1743390818.0.0.0'
        }
        response = self.session.post(login_URL, headers=headers, json=payload, cookies=cookies)
        response_json=response.json()

        if response_json.get('success')==True:
            logging.info(f"領取優惠碼成功 當前時間{current_time}")
            return True
        elif response_json.get('success')==False:
            error_message=response_json.get('message')
            logging.error(f"{error_message}")
            return False
    def Bonus_record_page(self,ws):
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-promotion-promoCode-claim-list"  
        start_time = datetime.now().strftime("%Y/%m/%d 00:00:00")
        end_time = datetime.now().strftime("%Y/%m/%d 23:59:59")
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_backend,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Tac-Trace-Id":"y#H-jHz_8Jv(1YU@",
            "Referer": "http://sit-admin2.tcg.com/311792",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG"
        }
        params={
            "claimStartTime":start_time,
            "claimEndTime":end_time,
            "isExport":"false",
            "merchantCode":"gi8viet",
            "customerName":self.username,
            "name":"carrine優惠碼" #優惠碼活動名稱寫死 要搜全部的話就把這行拿掉

        }
        cookies = {
            "language": "zh_CN",
        }
        try:
            response=requests.get(API_URL2, headers=headers, params=params, cookies=cookies, verify=False)

            response_data = response.json()
            if response_data.get("success") == True:
                self.record_data_list=response_data.get('value',[])
                for promo_codes in self.record_data_list:
                    promo_code=promo_codes.get("promoCode")
                    for rows in reversed(list(ws.iter_rows(values_only=False))):
                        if rows[0].value == self.username and rows[2].value == promo_code:
                            rows[8].value = "派發紀錄有資料"
                            break
                return True
            else:
                logging.error("後台查詢失敗")
                return False
            
        except Exception as e:
            logging.error(f"Exception 發生: {e}")
    def proccess_all_promoCode(self,ws):
        update_result='沒有資料'
        success_count=0
        bonusAmount = 1000
        bonusPointAmount = 30
        ticketQuantity = 3
        random_ticket=random.choice([1004007,1004006,1004008,1004010,1004009,1010009])
        ticketQuantity=3
        self.get_promo_code_list()
        for item in self.PromoCode_list:
            promoCode=item.get("promoCode")
            description=item.get("description","")
            if description!='carrine優惠碼':
                continue
            success=self.click_promo_code(promoCode)
            if success:
                success_count+=1
                update_result='成功領取優惠碼'
                bonus_record='紅利派發紀錄更新'  
                logging.info(f"領取第{success_count}組優惠碼成功") 
            else:
                bonus_record='紅利派發紀錄更新失敗'  
                update_result='領取優惠碼失敗'
        
            ws.append([
            self.username,
            'carrine優惠碼',
            promoCode,
            bonusAmount,
            bonusPointAmount,
            random_ticket,
            ticketQuantity,
            update_result,
            bonus_record
        ])
if __name__ == "__main__":

    wb=Workbook()
    ws=wb.active
    ws.title="優惠碼領取結果"
    ws.append(["玩家帳號","活動名稱", "優惠碼ID", "紅利金額", "積分", "票卷", "票卷張數","優惠碼領取狀態", "派發紀錄"])
    username_list=['cccc333','yyw1111','kkkk888','swow999','yyy771','nnn000','nnn111','nnn222','cccc333','ggg777']
    for name in username_list:
    #填入玩家帳號
        credential_frontend = {
            "username": name,
            "password": "123qwe"
        }
        credential_Backend = {
            "operatorName": "carrine03",
            "password": "Test@1234"
        }
        run_time="12:19"
        try:    
            frontend = Frontend(credential_frontend,credential_Backend)
            if frontend.token:
                logging.info(f"登入成功 Token: {frontend.token}")
                #frontend.click_promo_code()
                #schedule.every().day.at(f"{run_time}").do(frontend.click_promo_code,promo)
                frontend.proccess_all_promoCode(ws)
                frontend.Bonus_record_page(ws)
                time.sleep(1)
            else:
                logging.error("登入失敗 無法取得Token")
        
        except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")
    report_path=os.path.join(f"bonus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    wb.save(report_path)   
    
            

    