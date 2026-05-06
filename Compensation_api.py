import requests
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def Compensation_lucky_bet(round_id):
    URL=f"http://10.80.1.20:7001/promo-rd/resources/compensation/lucky_bet/{round_id}?isForce=false"
    header={
        "accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br"
    }
    respone=requests.post(URL,headers=header,verify=False)
    if respone.status_code==200:
        return True
    else:
        return False
    
def main(round_id):
    
    if round_id:
        logging.info(f"拿到round_ID: {round_id}")
        if Compensation_lucky_bet(round_id):
            return True
        else:
            return False
    else:
        logging.error("沒有拿到round_ID")
        return False