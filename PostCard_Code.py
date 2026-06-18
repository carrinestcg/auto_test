import requests,logging
from datetime import datetime,timedelta
import requests
import logging
import oracledb
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class PostCard:
    def __init__(self,credential:dict):
        self.credential=credential
        self.token=self.get_token()
    def header(self,merchantCode):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Language": "zh_CN",
            "Merchant": merchantCode,
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/20000",
            "customTimezone": "Etc/GMT-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": merchantCode,
            "platform": "TCG"
            }
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


    def DB_connect(self,SQL):
        host="10.81.1.11"
        port = 1521              
        service_name = "tcgsit"
        username = "TCG_MCSDB"
        password = "Jv7UrDc7rsqJ87Km"

        dsn=f"{host}:{port}/{service_name}"

        conn=oracledb.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        cursor=conn.cursor()
        cursor.execute(f"{SQL}")
        rows=cursor.fetchall()
        try:
            if rows:
                colums=[]
                for desc in cursor.description:
                    colums.append(desc[0])
                for row in rows:
                    print("="*60)
                    print("資訊")
                    print("="*60)
                    for col,val in zip(colums,row):
                        if isinstance(val,datetime):
                            val_str=val.strftime('%Y-%m-%d %H:%M:%S')
                        elif val==" ":
                            val_str='(空白)'
                            
                        elif val is None:
                            val_str='NULL'
                            
                        else:
                            val_str=str(val)
                        
                        print(f"{col:25s}: {val_str}")
                        
            else:
                logging.info("查無資料")
            return str(rows[0][0])
                
        except oracledb.DatabaseError as e:
            logging.error(f"❌ 資料庫錯誤: {e}")
        except Exception as e:
            logging.error(f"❌ 未預期的錯誤: {str(e)}")
        finally:
            if cursor in locals() and cursor:
                cursor.close()
            if conn in locals() and conn:
                conn.close()
      
    def request_code(self,username):
        customer_id=self.DB_connect(f"SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='gi8viet@{username}'")
        URL="http://10.81.1.88:8084/promo-fe/resources/postcard_code/request_code"

        header={
            "Content-Type":"application/json",
            "CustomerId":customer_id,
            "CustomerIP":"100.100.100.100"
        }
        
        resposne=requests.post(URL,headers=header,verify=False)
        resposne_json=resposne.json()
        if resposne_json.get("success"):
            value=resposne_json.get("value")
            postcardCode=value.get("postcardCode")
            logging.info(postcardCode)
            return postcardCode
        
        else:
            logging.error(f"{resposne.text}")
            return None
            
    def Search_request_code(self,postcardCode,merchantCode):
        try:
            API_URL="http://sit-admin2.tcg.com/tac/api/relay/get/promo-promotion-postcard-code-claim-search-code"
            param={
                "postcardCode":postcardCode,
                "status":"U",
                "pid":247814
            }
            headers = self.header(merchantCode)
            
            response=requests.get(API_URL, params=param,verify=False, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            logging.info(f"Search 完整回傳: {response_data}")
            if not response_data.get("success"):
                logging.error(f"API 回傳失敗: {response_data}")
                return None
            if response_data.get("success"):
                value=response_data.get("value")
                claimId=value.get("claimId")
                if claimId:
                    logging.info(f"拿到claimId{claimId}")
                    return claimId
                else:
                    logging.error("沒有拿到claimId")

            else:
                logging.error(response_data)
                return None
        except Exception as e:
            logging.error(f"{e}")
            return False
        
    def Approve_request_code(self,claimId,merchantCode):
        try:
            API_URL="http://sit-admin2.tcg.com/tac/api/relay/put/promo-promotion-postcard-code-claim-approve?pid=247815"
            
            headers = self.header(merchantCode)
            payload={
                "claimId": claimId,
                "status": "A"
            }
            cookies = {
            "language": "zh_CN"
            }
            response=requests.put(API_URL, json=payload,cookies=cookies,verify=False, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("success"):
                logging.info("成功審核")
                return True
            else:
                logging.error("審核失敗")
                return False
                
        except Exception as e:
            logging.error(f"{e}")
            return False
    def implement(self,username,merchantCode):
        
        postcardCode=self.request_code(username)
        claimId=self.Search_request_code(postcardCode,merchantCode)
        result = self.Approve_request_code(claimId,merchantCode)
        if result:
            return True
        else:
            return False
        
def main(username,merchantCode):
    if isinstance(merchantCode, list):
        merchantCode = merchantCode[0]
    print(merchantCode)
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
        }
    try:
        merchantCode=str(merchantCode)
        b_end=PostCard(credential)
        if b_end.token:
            if b_end.implement(username,merchantCode):
                return True
            else:
                return False

    except Exception as e:
        logging.error(e)
        