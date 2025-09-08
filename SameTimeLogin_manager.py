import requests,logging
import threading
import concurrent.futures,time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def run_operator(credential):
    try:
        b_end = B_end(credential)
        if b_end.token:
            b_end.implement()
        else:
            logging.error(f"[{credential['operatorName']}] 登入失敗 無法取得Token")
    except Exception as e:
        logging.error(f"[{credential['operatorName']}] 執行時發生錯誤: {e}")


class B_end:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.password=''
        self.credential=credential  
        self.token=self.get_token(credential['operatorName'],credential['password'])
        self.token_data=self.token
        self.record_data_list=[]
        self.claimid_list=[]
        self.success_count=0
        self.claimid=''
        self.lock=threading.Lock()
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
            "Merchant": self.credential["Merchant"],
            "MerchantCode": self.credential["MerchantCode"],
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

    def preview(self):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-lucky-bet-preview-task"
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Merchant": self.credential["Merchant"],
            "MerchantCode": self.credential["MerchantCode"],
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/24784",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "language": "zh_CN",
            "platform": "TCG",
            "Tac-Trace-Id":"PBVkC@!8s(QEn70G"
        }
        payload={
                "startTime": 1754035227900,
                "gamingMappingEnabled": "N",
                "gameMappings": None,
                "scheduleType": "HOURLY",
                "scheduleInterval": 1,
                "claimLimitType": "FIXED",
                "claimLimitConfigs": [
                    {
                        "amount": None,
                        "limitCount": 5
                    }
                ],
                "totalClaimLimitEnabled": "N",
                "totalClaimLimitCount": 0,
                "minValidBetAmt": 1,
                "bonusType": "FIXED",
                "ruleType": "LAST_DIGIT",
                "rewardConfigs": [
                    {
                        "rewardAmountLimit": None,
                        "winningRule": "89",
                        "bonus": 5,
                        "point": 5,
                        "turnoverMultiplier": 5,
                        "betAmountMultiplier": None,
                        "betNumCount": None,
                        "betNumTarget": None,
                        "ticketRewards": [
                            {
                                "ticketId": 1099016,
                                "ticketQuantity": 1
                            }
                        ]
                    }
                ]
            }
        response=requests.post(URL,headers=headers,json=payload,verify=False)
        response_data=response.json()
        if response_data.get("success")==True:
            value=response_data.get("value")
            task_id=value["taskId"]
            logging.info(f"task_id={task_id}")
            return task_id
        else:
            logging.info(response_data)
            logging.error("沒有拿到task_id")

    def get_task_id(self,task_id):
        URL=f"http://sit-admin2.tcg.com/tac/api/relay/get/promo-promotion-lucky-bet-preview-by-taskId?taskId={task_id}"
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Merchant": self.credential["Merchant"],
            "MerchantCode": self.credential["MerchantCode"],
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/24784",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "language": "zh_CN",
            "platform": "TCG",
            "Tac-Trace-Id":"PBVkC@!8s(QEn70G"
        }
        params={
                "taskId":task_id
            }
        response=requests.get(URL,headers=headers,params=params,verify=False)
        response_data=response.json()
        if response_data.get("success")==True:
            value=response_data.get("value")
            logging.info(f"value={value}")
            logging.info(f"{response_data}")
            return value
        else:

            return None
    def implement(self):
        time.sleep(1)
        task_id=self.preview()
        if task_id:
            result=self.get_task_id(task_id)
            if result:
                logging.info("試算成功")
        

    
def main():

    credentials = [
        {
            "operatorName": "carrine03",
            "password": "Test@1234",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
        },
        {
            "operatorName": "carrine01",
            "password": "Test@1234",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            #"Merchant": "huamei",
            #"MerchantCode": "huamei",
        }
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(credentials)) as executor:
        future= [executor.submit(run_operator, credential) for credential in credentials]
        concurrent.futures.wait(future)
    logging.info("所有品牌管理員試算操作完成")

            



   