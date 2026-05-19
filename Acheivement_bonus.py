import requests
import logging
import urllib3
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def Achievement_bonus(promotionId, CustomerIP, CustomerId ):
    URL="http://10.80.1.19:8084/promo-fe/resources/achievement/claim"
    header={
        "accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",
        "CustomerIP": CustomerIP,
        "Language": "CN",
        "CustomerId": CustomerId
    }
    payload={
        "promotionId": promotionId
    }
    respone=requests.post(URL,headers=header,json=payload, verify=False)
    respone_json=respone.json()
    if respone.status_code==200:
        value=respone_json.get("value")
        claimedMoney=value.get("claimedMoney")
        claimedPoint=value.get("claimedPoint")
        claimedTickets=value.get("claimedTickets")
        logging.info(f"領取成功: {claimedMoney} {claimedPoint}, {claimedTickets}")
        return claimedMoney, claimedPoint, claimedTickets
    else:
        logging.info(f"領取失敗 原因:{respone_json}")
        return None, None, None
    
def main(promotionId, CustomerId):
    
    if promotionId:
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        logging.info(f"拿到promotionId: {promotionId}")
        claimedMoney, claimedPoint, claimedTickets= Achievement_bonus(promotionId,CustomerIP,CustomerId)
        if claimedMoney and claimedPoint and claimedTickets:
            return claimedMoney, claimedPoint, claimedTickets
        else:
            return None, None, None
    else:
        logging.error("沒有拿到round_ID")
        return None, None, None