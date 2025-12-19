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
    def unit_time(self):
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        return unit_time
    def header(self,CustomerId):
        unit_time=self.unit_time()
        return{
            'Content-Type': 'application/json',
            'X-Timestamp':unit_time,
            'Connection': 'keep-alive',
            'Language': 'CN',
            'CustomerId':CustomerId,
            'CustomerIP':'10.180.99.19',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
           
        }
        
    def __init__(self):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.PromoCode_list=''
        self.promoID=''
        self.i=0
        self.record_data_list=''
    
    def get_promo_code_list(self,CustomerId):
       
        login_URL="http://10.80.1.20:7001/promo-fe/resources/promo_code"
        headers=self.header(CustomerId)
        
        response = self.session.get(login_URL, headers=headers, verify=False)
        response_json=response.json()

        if response_json.get('success')==True:
            PromoCode_list=response_json.get("value",[])
            return PromoCode_list
        else:
            logging.error(f"沒拿到優惠碼ID")
            return 
    def click_promo_code(self,promoCode,CustomerId):
       
        login_URL="http://10.80.1.20:7001/promo-fe/resources/promo_code/claim"
        unit_time=self.unit_time()
        headers=self.header(CustomerId)
        payload={
             "promoCode": promoCode
        }
        
        response = self.session.post(login_URL, headers=headers, json=payload)
        response_json=response.json()
        print(response_json)

        if response.status_code=='200':
            logging.info(f"領取優惠碼成功")
            return True
        elif response_json.get('success')==False:
            error_message=response_json.get('message')
            logging.error(f"{error_message}")
            return False
    def proccess_all_promoCode(self,ws,customer_id):
        update_result='沒有資料'
        PromoCode_list=self.get_promo_code_list(customer_id)
        filter_list=[]
        success = False
        success_count=0
        for item in PromoCode_list:
            promoName=item.get("promoName","")
            if  promoName!='CCD_Promo code_01':
                continue
            filter_list.append(item)
            promo_dict=random.choice(filter_list)
            promoCode=promo_dict["promoCode"]
            success=self.click_promo_code(promoCode,customer_id)

        if success:
            success_count+=1
            update_result='成功領取優惠碼'
            bonus_record='紅利派發紀錄更新'  
            logging.info(f"領取優惠碼{promoCode}成功") 
        else:
            bonus_record='紅利派發紀錄更新失敗'  
            update_result='領取優惠碼失敗'
    
            ws.append([
            self.username,
            'carrine優惠碼',
            promoCode,
            update_result,
            bonus_record
            ])
            return success_count
            
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
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "language": "zh_CN",
            "noErrorNotice": "true",
            "platform": "TCG",
            "Tac-Trace-Id":"q02^1XO_0PfgK!xY",
            "Authorization": self.token_data,
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
    def get_remaincount_promocode(self,):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-promotion-promoCode-list"
        params={
            "merchantCode":"gi8viet",
            "status":"A",
            "pageNo":1,
            "pageSize":1000
        }
        headers=self.header()
        cookies = {
            "language": "zh_CN",
        }
        response=requests.get(URL,headers=headers,params=params,cookies=cookies,verify=False)
        response_json=response.json()
        if response_json.get("success")==True:
            value_list=response_json.get("value",[])
            for item in value_list:
                name=item.get("name","")
                if name=='carrine優惠碼':
                    remainingCountDaily=item.get("remainingCountDaily")
                    remainingCount=item.get("remainingCount")
                    return remainingCountDaily,remainingCount
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
    def Bonus_record_page(self,ws):
        API_URL2=f"http://sit-admin2.tcg.com/tac/api/relay/get/mcs-promotion-promoCode-claim-list"  
        start_time = datetime.now().strftime("%Y/%m/%d 00:00:00")
        end_time = datetime.now().strftime("%Y/%m/%d 23:59:59")
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token_data,
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
                print(response_data)
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

def main(username:str):
    wb=Workbook()
    ws=wb.active
    ws.title="優惠碼領取結果"
    ws.append(["玩家帳號","活動名稱", "優惠碼ID","優惠碼領取狀態", "派發紀錄"])
    
    total_claim_count=0
    dailyremain_count=0
    remainingCount=0
    credential_Backend = {
            "operatorName": "carrine03",
            "password": "Test@1234"
        }
    try:    
        backend = B_end(credential_Backend)
        if backend.token:
            
            customer_id=backend.search_customerid(username)
            str_customerid=str(customer_id)
            dailyremain_count,remainingCount=backend.get_remaincount_promocode()
            logging.info(f"當日剩餘次數{dailyremain_count}")
            logging.info(f"總剩餘次數{remainingCount}")

        
        try:   
            frontend = Frontend()
            
            success_count=frontend.proccess_all_promoCode(ws,str_customerid)
            total_claim_count+=success_count
        
        except Exception as e:
                logging.error(f"啟動時發生錯誤: {e}")
        time.sleep(0.5)
        backend.Bonus_record_page(ws)
        if backend.token:
            after_receive_remain_dailyremain_count,after_receive_remainingCount=backend.get_remaincount_promocode()
            logging.info(f"更新後的當日剩餘次數{after_receive_remain_dailyremain_count}")
            logging.info(f"總剩餘次數{remainingCount}")
            assert (dailyremain_count-after_receive_remain_dailyremain_count)==total_claim_count
            assert (remainingCount-after_receive_remainingCount)==total_claim_count
            
        
            
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")
         
    report_path=os.path.join(f"bonus_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    wb.save(report_path)   

    
            

    