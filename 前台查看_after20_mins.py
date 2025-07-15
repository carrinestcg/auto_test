import requests,logging,time,yaml,os,random
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def __init__(self,credential_fe:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential_fe=credential_fe
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login_frontend(credential_fe['username'],credential_fe['password'])
        self.type=''
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
    def get_mission_id(self):
            if not self.is_token_valid():
                logging.info("token 過期, 重新登入")
                self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
            if self.token is None:
                return
            current_time=datetime.now()
            unit_time=str(int(current_time.timestamp()*1000))
            login_URL=f"http://www.sit-gi8viet.com/wps/relay/MCSFE_getMissionSummaryDetails"

            headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': 'http://www.sit-gi8viet.com',
                    'ModuleId': 'MISSIONLB3',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',  
                    'x-timestamp': unit_time     
                }
            params={
                    "status": "O",
                    "page":1,
                    "size":5,
                    "_":unit_time, 
            }
            cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
                
            response=self.session.get(login_URL,headers=headers,params=params,cookies=cookies,verify=False)
            response_json=response.json()   
            if response_json.get('success')==True:
                    value_data_list=response_json.get("value",{}).get("list", [])
                    for item in value_data_list:
                         title=item.get("title",[])     
                         if title=='Carrine_test':
                            mission_id=item.get("missionId")
                            logging.info(f"拿到mission_id:{mission_id}")
                            return mission_id

            else:
                    logging.error(f"api呼叫失敗")
                    success_fail+=1
           
    def get_mission_milestone(self,mission_id):
        bank_types=["WECHAT"] #PAYID
        for bank_type in bank_types:
            if not self.is_token_valid():
                logging.info("token 過期, 重新登入")
                self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
            if self.token is None:
                return
            current_time=datetime.now()
            unit_time=str(int(current_time.timestamp()*1000))
            login_URL=f"http://www.sit-gi8viet.com/wps/relay/MCSFE_getMissionMilestones"

            headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': 'http://www.sit-gi8viet.com/rng?page=JDB',
                    'ModuleId': 'MISSIONLB3',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',  
                    'x-timestamp': unit_time     
                }
            payload={
                    "missionId":mission_id,
                    "_":unit_time, 
            }
            cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
                
            response=self.session.get(login_URL,headers=headers,json=payload,cookies=cookies,verify=False)
            response_json=response.json()    
            if response_json.get('success')==True:
                    value_data_list=response_json.get("value",{})
                    for item in value_data_list:
                         title=item.get("title",[])
                         mission_id=item.get("missionId")       
                         if title=='Carrine_test':
                            logging.info(f"拿到mission_id:{mission_id}")
                            return mission_id
                         else:
                             logging.error("沒有找到 Carrine_test的mission")

            else:
                    logging.error(f"api呼叫失敗")
                    success_fail+=1
           
    def get_mission_leaderBoard(self,mission_id,account:str):
            if not self.is_token_valid():
                logging.info("token 過期, 重新登入")
                self.get_token_login_frontend(self.credential_fe['username'],self.credential_fe['password'])
            if self.token is None:
                return
            current_time=datetime.now()
            unit_time=str(int(current_time.timestamp()*1000))
            login_URL=f"http://www.sit-gi8viet.com/wps/relay/MCSFE_getMissionLeaderboard"

            headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': 'http://www.sit-gi8viet.com?page=JDB',
                    'ModuleId': 'MISSIONLB3',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',  
                    'x-timestamp': unit_time     
                }
            params={
                    "missionId":mission_id,
                    "_":unit_time, 
            }
            cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
                
            response=self.session.get(login_URL,headers=headers,params=params,cookies=cookies,verify=False)
            response_json=response.json()   
            if response_json.get('success')==True:
                    value_data_list=response_json.get("value",{})
                    footer=value_data_list.get("footer")
                    rank=footer.get("rank")
                    reachedValue=footer.get("reachedValue")
                    logging.info(f"{account}拿到rank:{rank}")
                    return rank,reachedValue
            else:
                        logging.error("沒有找到 Carrine_test的mission")
             
    
if __name__ == "__main__":

    password = "123qwe"
    #username="three444"
    credential_be = {
            "operatorName": "carrine03",
            "password": "Test@1234"
    }
    current_dir=os.path.dirname(__file__)
    yaml_path=os.path.join(current_dir,"config.yaml")
    with open(yaml_path,"r",encoding="utf-8") as f:
        config=yaml.safe_load(f)
    first_testing_account=config.get("first_testing_account")
    try:
        for account, rank in first_testing_account.items():
            expect_rank=rank.get("second_expect_rank")
            credential_fe = {
                    "username": account,
                    "password": password
                    }
            frontend = Frontend(credential_fe)
            if frontend.token:
                mission_id=frontend.get_mission_id()
                time.sleep(0.5)
                if mission_id:
                    actual_rank,reachedValue=frontend.get_mission_leaderBoard(mission_id,account)
                    if actual_rank == expect_rank:
                        logging.info(f"{account} 投注金額{reachedValue} 名次正確 ✅（預期: {expect_rank}, 實際: {actual_rank}")
                    else:
                         logging.error(f"{account} 投注金額{reachedValue} 名次正確 名次錯誤 ❌（預期: {expect_rank}, 實際: {actual_rank}")
                    time.sleep(1)
                                   
            else:
                logging.error("登入失敗 無法取得Token")
            
    except Exception as e:
         logging.error(f"啟動錯誤{e}")