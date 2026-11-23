import requests
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def rescure_reward(merchantCode, date):
    URL="http://10.81.1.20:7001/promo-rd/resources/compensation/savior"
    header={
        "accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br"
    }
    params={
        "rewardType": "DAILY",
        "processDate" : date,
        "merchantCode" : merchantCode,
        "force" : True
        }
    respone=requests.post(URL,headers=header, params=params, verify=False)
    if respone.status_code==200:
        return True
    else:
        return False
    
def main(merchantCode, date):
    
    if merchantCode:
        logging.info(f"拿到merchantCode: {merchantCode}")
        if rescure_reward(merchantCode, date):
            logging.info(f"成功調用救援金API:")
            return True
        else:
            logging.error(f"調用救援金失敗:")
            return False
    else:
        logging.error("沒有拿到setting_ID")
        return False