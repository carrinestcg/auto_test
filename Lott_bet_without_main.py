import requests,logging,os,yaml,time
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential=credential
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login(credential['username'],credential['password'])
        self.type=''
    def get_token_login(self, username, password):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url='http://www.sit2.sit-gi8viet.com/wps/session/login/unsecure'
            
            headers = {
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
            }
            login_data={
                'username':username,
                'password':password
            } 
            
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
    def launch_game(self):
        API_URL="http://www.sit-gi8viet.com/wps/game/launchGame"   
        headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': 'http://www.sit-gi8viet.com/lotto-vn/t3/games/5913',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                }
        params={
            "device":"WEB",
            "lottoArea":"VN",
            "lottoPrizeMode":"Lott",
            "launchMode":"LOTT",
            "language":"EN",
            "lottoView":"betting",
            "lottoGameCode":"TESTTHAI3"
        }
        cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
        request_data=self.session.get(API_URL,headers=headers,params=params,cookies=cookies,verify=False)
        json_data = request_data.json()
        if json_data.get("success")==True:
            logging.info("成功開啟遊戲")
            return True
        else :
            logging.info("開啟遊戲失敗")
            return False
    def get_prize_mode(self):
        API_URL="http://www.sit-gi8viet.com/lotto-vn/lgw/numeros/near?gameId=5910"   
        headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': 'http://www.sit-gi8viet.com/lotto-vn/t3/games/5910',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                }
        
        cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
        
        request_data=self.session.get(API_URL,headers=headers,cookies=cookies,verify=False)
        json_data = request_data.json()
        currentnumero_info=json_data.get("currentNumero",{})
        numero=currentnumero_info.get("numero")
        game_id=currentnumero_info.get("gameId")
        if numero and game_id:
            logging.info(f"拿到該彩票場次資訊{numero} {game_id}")
            return numero,game_id
        else:
            logging.info(f"沒有拿到該彩票場次資訊{numero} {game_id}")
                    
        return None,None
    def bet_func(self,numero,game_id,amount):
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        API_URL=f"http://www.sit-gi8viet.com/lotto-vn/lgw/betting?t={unit_time}"   
        headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://www.sit-gi8viet.com',
                    'Referer': f'http://www.sit-gi8viet.com/lotto-vn/t3/games/{game_id}',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                }
        payload={

                "prizeMode": "Lott",
                "device": "WEB",
                "contents": [
                    {
                        "gameId": game_id,
                        "winStop": False,
                        "playId": 2057,
                        "bettingContent": "0_4_1",
                        "singleBetPrice": amount,
                        "bettingApproach": 1,
                        "bettingSlip": None,
                        "numero": [
                            {
                                "numero": numero,
                                "multiple": 1
                            }
                        ]
                    }
                ]
            }
        cookies={
                    'SHELL_deviceId': '8c5bdbd3-b2cd-b350-4c4e-5967bb9d7966',
                }
        request_data=self.session.post(API_URL,headers=headers,cookies=cookies,json=payload,verify=False)
        if request_data.status_code==200:
            return True
        else:
            return False
def implement(username,password,amount):
        
            try:    
                credential = {
                    "username": username,
                    "password": password
                }
                frontend = Frontend(credential)
                if frontend.token:
                    frontend.launch_game()
                    numero,game_id=frontend.get_prize_mode()
                    if numero and game_id :
                        issuccess=frontend.bet_func(numero,game_id,amount)
                        if issuccess:
                            logging.info(f"成功投注彩票{amount}")
                            time.sleep(1)
                        else:
                            logging.error("投注彩票失敗")
                    else:
                        logging.error("沒有拿到numero")
                else:
                    logging.error("登入失敗 無法取得Token")
            
            except Exception as e:
                logging.error(f"啟動時發生錯誤: {e}")

        