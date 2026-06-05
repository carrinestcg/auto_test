import requests
import logging
import urllib3
import random
import concurrent.futures

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def Achievement_bonus(promotionId, CustomerIP, CustomerId):
    URL = "http://10.80.1.88:8084/promo-fe/resources/achievement/claim"
    header = {
        "accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "CustomerIP": CustomerIP,
        "Language": "CN",
        "CustomerId": CustomerId
    }
    payload = {
        "promotionId": promotionId
    }
    response = requests.post(URL, headers=header, json=payload, verify=False)
    response_json = response.json()

    if response.status_code == 200:
        value = response_json.get("value")
        claimedMoney = value.get("claimedMoney")
        claimedPoint = value.get("claimedPoint")
        claimedTickets = value.get("claimedTickets")
        logging.info(f"領取成功: {claimedMoney} {claimedPoint}, {claimedTickets}")
        return claimedMoney, claimedPoint, claimedTickets
    else:
        logging.error(f"領取失敗 原因: {response_json}")
        return None, None, None


def get_unclaim_Quest(promotionId, CustomerIP, CustomerId, promoType):
    URL = "http://10.80.1.88:8084/promo-fe/resources/quest/unclaim_list"
    header = {
        "accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "CustomerIP": CustomerIP,
        "Language": "CN",
        "CustomerId": CustomerId
    }
    params = {
        "promotionId": promotionId
    }

    response = requests.get(URL, headers=header, params=params, verify=False)
    response_json = response.json()

    if response.status_code == 200:
        value = response_json.get("value") or {}

        if promoType == 2:
            claims = value.get("claims") or []
            if not isinstance(claims, list):
                logging.warning("claims 非 list，無法解析任務 claimId: %r", type(claims))
                return []
            claimID_list = []
            for item in claims:
                if not isinstance(item, dict):
                    continue
                if item.get("claimStatus") == "CLAIMABLE":
                    claim_id = item.get("claimId")
                    if claim_id is not None:
                        claimID_list.append(claim_id)
            logging.info(f"找到 {len(claimID_list)} 個 claimId: {claimID_list}")
            return claimID_list

        if promoType == 3:
            activity_resp = value.get("activityRewardListResp") or {}
            activities = activity_resp.get("activities") or []
            activity_ids = []
            for activity in activities:
                if not isinstance(activity, dict):
                    continue
                activity_id = activity.get("activityId")
                if activity_id is not None:
                    activity_ids.append(activity_id)
            logging.info(f"找到 {len(activity_ids)} 個 activityId: {activity_ids}")
            return activity_ids

    else:
        logging.error(f"取得任務列表失敗 原因: {response_json}")
        return []


def receive_quest_bonus_single(CustomerIP, CustomerId, claimid):
    URL = "http://10.80.1.20:7001/promo-fe/resources/promo_claim"
    header = {
        "accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "CustomerIP": CustomerIP,
        "Language": "CN",
        "CustomerId": CustomerId
    }
    payload = {
        "claimId": claimid,
        "promotionType": "QUEST"
    }

    response = requests.post(URL, headers=header, json=payload, verify=False)
    response_json = response.json()

    if response.status_code == 200:
        value = response_json.get("value")
        claimedMoney = value.get("claimedMoney")
        claimedPoint = value.get("claimedPoint")
        claimedTickets = value.get("claimedTickets")
        logging.info(f"[claimId: {claimid}] 領取成功: 金額={claimedMoney}, 點數={claimedPoint}, 票券={claimedTickets}")
        return claimedMoney, claimedPoint, claimedTickets
    else:
        logging.error(f"[claimId: {claimid}] 領取失敗 原因: {response_json}")
        return None, None, None


def receive_activity_bonus_single(CustomerIP, CustomerId, activity_id):
    URL = "http://10.80.1.88:8084/promo-fe/resources/quest/claim/activity"
    header = {
        "accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "CustomerIP": CustomerIP,
        "Language": "CN",
        "CustomerId": CustomerId
    }
    payload = {
        "activityId": activity_id
    }

    response = requests.post(URL, headers=header, json=payload, verify=False)
    response_json = response.json()

    if response.status_code == 200:
        value = response_json.get("value")
        claimedMoney = value.get("claimedMoney")
        claimedPoint = value.get("claimedPoint")
        claimedTickets = value.get("claimedTickets")
        logging.info(f"[activityId: {activity_id}] 領取成功: 金額={claimedMoney}, 點數={claimedPoint}, 票券={claimedTickets}")
        return claimedMoney, claimedPoint, claimedTickets
    else:
        logging.error(f"[activityId: {activity_id}] 領取失敗 原因: {response_json}")
        return None, None, None


def main(player_list, promoType, promotionId):
    
    if not promotionId:
        logging.error("沒有拿到 promotionId")
        return

    if promoType == 2:

        # 每個玩家各自查自己的 claimId
        player_tasks = []
        for player in player_list:
            CustomerIP = ".".join(str(random.randint(0, 255)) for _ in range(4))
            claimID_list = get_unclaim_Quest(promotionId, CustomerIP, player["CustomerId"], promoType)

            if not claimID_list:
                logging.info(f"[CustomerId: {player['CustomerId']}] 沒有可領取的 claimId")
                continue

            for claimid in claimID_list:
                player_tasks.append((CustomerIP, player["CustomerId"], claimid))

        if not player_tasks:
            logging.info("所有玩家都沒有可領取的 claimId")
            return

        logging.info(f"=== 開始並行測試，共 {len(player_tasks)} 個領取任務 ===")
        for task in player_tasks:
            logging.info(f"  CustomerId: {task[1]}, claimId: {task[2]}")

        # 所有玩家同時發送各自的領取請求
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(player_tasks)) as executor:
            futures = {
                executor.submit(receive_quest_bonus_single, ip, cid, claimid): (cid, claimid)
                for ip, cid, claimid in player_tasks
            }
            for future in concurrent.futures.as_completed(futures):
                cid, claimid = futures[future]
                try:
                    result = future.result()
                    results.append({
                        "CustomerId": cid,
                        "claimId": claimid,
                        "result": result
                    })
                except Exception as e:
                    logging.error(f"[CustomerId: {cid}][claimId: {claimid}] 執行時發生錯誤: {e}")

        # 統計結果
        success_list = [r for r in results if r["result"][0] is not None]
        fail_list = [r for r in results if r["result"][0] is None]

        logging.info(f"=== 測試結果 ===")
        logging.info(f"總計: {len(results)} 筆")
        logging.info(f"成功: {len(success_list)} 筆")
        logging.info(f"失敗: {len(fail_list)} 筆")

        if fail_list:
            logging.warning(f"⚠️ 有失敗的領取，可能發生 SQL 衝突！")
            for r in fail_list:
                logging.warning(f"  CustomerId: {r['CustomerId']}, claimId: {r['claimId']}")


# 執行
player_list = [
    {"CustomerId": "9590331"},
    {"CustomerId": "6697484"},
]

main(player_list, promoType=2, promotionId="4574108")