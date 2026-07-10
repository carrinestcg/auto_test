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
    try:
        respone_json=respone.json()
    except ValueError:
        logging.error("成就獎勵 API 回傳非 JSON: status=%s body=%s", respone.status_code, respone.text[:500])
        return None, None, None
    if respone.status_code==200:
        value=respone_json.get("value") or {}
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
        "CustomerId": str(CustomerId),
    }
    params={
        "promotionId": promotionId
    }
    respone=requests.get(URL,headers=header,params=params, verify=False)
    try:
        respone_json=respone.json()
    except ValueError:
        logging.error("任務列表 API 回傳非 JSON: status=%s body=%s", respone.status_code, respone.text[:500])
        return []
    if respone.status_code==200:
        value=respone_json.get("value") or {}
        if promoType==2:
            claims=value.get("claims") or []
            claimID_list=[]
            for claimid in claims:
                if not isinstance(claimid, dict):
                    continue
                if claimid.get("claimStatus") == "CLAIMABLE":
                    claim_id = claimid.get("claimId")
                    if claim_id is not None:
                        claimID_list.append(claim_id)
            logging.info(f"找到 {len(claimID_list)} 個 claimId: {claimID_list}")
            return claimID_list
        elif promoType==3:
            activityRewardListResp=value.get("activityRewardListResp") or {}
            aactivities=activityRewardListResp.get("activities") or []
            activity_ids = []
            for activity in aactivities:
                if not isinstance(activity, dict):
                    continue
                activity_id = activity.get("activityId")
                if activity_id is not None:
                    activity_ids.append(activity_id)
            logging.info(f"找到 {len(activity_ids)} 個 activityId: {activity_ids}")
            return activity_ids
    logging.info(f"取得任務列表失敗 原因:{respone_json}")
    return []

def receive_quest_bonus(CustomerIP, CustomerId, claimID_list):
    if not claimID_list:
        logging.info("沒有可領取的 claimId")
        return None, None, None

    claimedMoney = claimedPoint = claimedTickets = None
    for claimid in claimID_list:
        URL="http://10.81.1.20:7001/promo-fe/resources/promo_claim"
        header={
            "accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "CustomerIP": CustomerIP,
            "Language": "CN",
            "CustomerId": str(CustomerId),
        }
        payload={
            "claimId": claimid,
            "promotionType": "QUEST"
        }
        respone=requests.post(URL,headers=header,json=payload, verify=False)
        try:
            respone_json=respone.json()
        except ValueError:
            logging.error("任務領取 API 回傳非 JSON: status=%s body=%s", respone.status_code, respone.text[:500])
            return None, None, None
        if respone.status_code==200:
            value=respone_json.get("value") or {}
            claimedMoney=value.get("claimedMoney")
            claimedPoint=value.get("claimedPoint")
            claimedTickets=value.get("claimedTickets")
            logging.info(f"[claimId: {claimid}] 領取成功: {claimedMoney} {claimedPoint}, {claimedTickets}")
        else:
            logging.info(f"[claimId: {claimid}] 領取失敗 原因:{respone_json}")
            return None, None, None
    return claimedMoney, claimedPoint, claimedTickets

def receive_activity_bonus(CustomerIP, CustomerId, activity_list):
    if not activity_list:
        logging.info("沒有可領取的 activityId")
        return None, None, None

    claimedMoney = claimedPoint = claimedTickets = None
    for activity in activity_list:
        URL="http://10.81.1.88:8084/promo-fe/resources/quest/claim/activity"
        header={
            "accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "CustomerIP": CustomerIP,
            "Language": "CN",
            "CustomerId": str(CustomerId),
        }
        payload={
            "activityId": activity,
        }
        respone=requests.post(URL,headers=header,json=payload, verify=False)
        try:
            respone_json=respone.json()
        except ValueError:
            logging.error("活躍度領取 API 回傳非 JSON: status=%s body=%s", respone.status_code, respone.text[:500])
            return None, None, None
        if respone.status_code==200:
            value=respone_json.get("value") or {}
            claimedMoney=value.get("claimedMoney")
            claimedPoint=value.get("claimedPoint")
            claimedTickets=value.get("claimedTickets")
            logging.info(f"[activityId: {activity}] 領取成功: {claimedMoney} {claimedPoint}, {claimedTickets}")
        else:
            logging.info(f"[activityId: {activity}] 領取失敗 原因:{respone_json}")
            return None, None, None
    return claimedMoney, claimedPoint, claimedTickets
def _normalize_promo_type(promoType):
    try:
        return int(promoType)
    except (TypeError, ValueError):
        return None

def main(CustomerId, promoType, promotionId):
    promoType = _normalize_promo_type(promoType)
    if CustomerId is None:
        logging.error("沒有拿到 CustomerId")
        return None, None, None

    if promoType == 1:
        if promotionId:
            CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
            logging.info(f"拿到promotionId: {promotionId}")
            claimedMoney, claimedPoint, claimedTickets= Achievement_bonus(promotionId,CustomerIP,str(CustomerId))
            if claimedMoney is not None or claimedPoint is not None or claimedTickets is not None:
                return claimedMoney, claimedPoint, claimedTickets
            return None, None, None
        logging.error("沒有拿到promotionId")
        return None, None, None

    elif promoType == 2:
        if promotionId:
            CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
            logging.info(f"拿到promotionId: {promotionId}")
            claimID_list = get_unclaim_Quest(promotionId, CustomerIP, CustomerId, promoType)
            if claimID_list:
                claimedMoney, claimedPoint, claimedTickets = receive_quest_bonus(CustomerIP, CustomerId, claimID_list)
                if claimedMoney is not None or claimedPoint is not None or claimedTickets is not None:
                    return claimedMoney, claimedPoint, claimedTickets
            return None, None, None
        logging.error("沒有拿到promotionId")
        return None, None, None
    elif promoType == 3:
        if promotionId:
            CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
            logging.info(f"拿到promotionId: {promotionId}")
            activity_list = get_unclaim_Quest(promotionId, CustomerIP, CustomerId, promoType)
            if activity_list:
                claimedMoney, claimedPoint, claimedTickets = receive_activity_bonus(CustomerIP, CustomerId, activity_list)
                if claimedMoney is not None or claimedPoint is not None or claimedTickets is not None:
                    return claimedMoney, claimedPoint, claimedTickets
            return None, None, None
        logging.error("沒有拿到promotionId")
        return None, None, None

    logging.error("不支援的 promoType: %s", promoType)
    return None, None, None
