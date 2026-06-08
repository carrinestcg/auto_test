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
    URL="http://10.81.1.88:8084/promo-fe/resources/achievement/claim"
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
    
def get_unclaim_Quest(promotionId, CustomerIP, CustomerId, promoType):
    URL="http://10.81.1.88:8084/promo-fe/resources/quest/unclaim_list"
    header={
        "accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",
        "CustomerIP": CustomerIP,
        "Language": "CN",
        "CustomerId": CustomerId
    }
    params={
        "promotionId": promotionId
    }
    claimID_list=[]
    respone=requests.get(URL,headers=header,params=params, verify=False)
    respone_json=respone.json()
    if respone.status_code==200:
        value=respone_json.get("value")
        claims=value.get("claims", [])
        activityRewardListResp=value.get("activityRewardListResp", {})
        aactivities=activityRewardListResp.get("activities", [])
        if promoType==2:
            for claimid in claims:
                claimStatus=claimid.get("claimStatus")
                if claimStatus == "CLAIMABLE":
                    claimId=claimid.get("claimId")
                    claimID_list.append(claimId)
            return claimID_list
        elif promoType==3:
            activity_ids = []
            for activity in aactivities:
                activity_id = activity.get("activityId")
                activity_ids.append(activity_id)
            return activity_ids
    else:
        logging.info(f"領取失敗 原因:{respone_json}")
        return None, None, None
def receive_quest_bonus(CustomerIP, CustomerId, claimID_list):
    for claimid in claimID_list:
        URL="http://10.81.1.20:7001/promo-fe/resources/promo_claim"
        header={
            "accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "CustomerIP": CustomerIP,
            "Language": "CN",
            "CustomerId": CustomerId
        }
        payload={
            "claimId": claimid,
            "promotionType": "QUEST"
        }
        respone=requests.post(URL,headers=header,json=payload, verify=False)
        respone_json=respone.json()
        if respone.status_code==200:
            value=respone_json.get("value")
            claimedMoney=value.get("claimedMoney")
            claimedPoint=value.get("claimedPoint")
            claimedTickets=value.get("claimedTickets")
            logging.info(f"領取成功: {claimedMoney} {claimedPoint}, {claimedTickets}")
        
        else:
            logging.info(f"領取失敗 原因:{respone_json}")
            return None, None, None
    return claimedMoney, claimedPoint, claimedTickets

def receive_activity_bonus(CustomerIP, CustomerId, activity_list):
    for activity in activity_list:
        URL="http://10.81.1.88:8084/promo-fe/resources/quest/claim/activity"
        header={
            "accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "CustomerIP": CustomerIP,
            "Language": "CN",
            "CustomerId": CustomerId
        }
        payload={
            "activityId": activity,
            
        }
        respone=requests.post(URL,headers=header,json=payload, verify=False)
        respone_json=respone.json()
        if respone.status_code==200:
            value=respone_json.get("value")
            claimedMoney=value.get("claimedMoney")
            claimedPoint=value.get("claimedPoint")
            claimedTickets=value.get("claimedTickets")
            logging.info(f"領取成功: {claimedMoney} {claimedPoint}, {claimedTickets}")
        
        else:
            logging.info(f"領取失敗 原因:{respone_json}")
            return None, None, None
    return claimedMoney, claimedPoint, claimedTickets
def main(CustomerId, promoType, promotionId):
    if promoType== 1:
        if promotionId:
            CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
            logging.info(f"拿到promotionId: {promotionId}")
            claimedMoney, claimedPoint, claimedTickets= Achievement_bonus(promotionId,CustomerIP,CustomerId)
            if claimedMoney is not None and claimedPoint is not None:
                return claimedMoney, claimedPoint, claimedTickets
            else:
                return None, None, None
        else:
            logging.error("沒有拿到promotionId")
            return None, None, None
        
    elif promoType== 2:
        if promotionId:
            CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
            logging.info(f"拿到promotionId: {promotionId}")
            claimID_list= get_unclaim_Quest(promotionId,CustomerIP,CustomerId, promoType)
            if claimID_list is not None:
                claimedMoney, claimedPoint, claimedTickets=receive_quest_bonus(CustomerIP,CustomerId,claimID_list)
                if claimedMoney and claimedPoint and claimedTickets:
                    return claimedMoney, claimedPoint, claimedTickets
                else:
                    return None, None, None
            else:
                return False
        else:
            logging.error("沒有拿到promotionId")
            return None, None, None
    elif promoType== 3:
        if promotionId:
            CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
            logging.info(f"拿到promotionId: {promotionId}")
            activity_list= get_unclaim_Quest(promotionId,CustomerIP,CustomerId, promoType)
            if activity_list is not None:
                claimedMoney, claimedPoint, claimedTickets=receive_activity_bonus(CustomerIP,CustomerId,activity_list)
                if claimedMoney and claimedPoint and claimedTickets:
                    return claimedMoney, claimedPoint, claimedTickets
                else:
                    return None, None, None
            else:
                return False
        else:
            logging.error("沒有拿到promotionId")
            return None, None, None
