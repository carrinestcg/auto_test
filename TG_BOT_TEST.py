#!/usr/bin/env python3
"""
TG 紅包雨 - 上線後 Sanity Check
只驗證最關鍵路徑，不是完整回歸測試（完整案例已在上線前手動測過）。

用法：
    python sanity_check.py

執行前請確認下面 CONFIG 區塊：
- BASE_URL 指向正確環境（上線後應該是 production）
- PROMOTION_ID 們對應到當時可用的真實活動
- 玩家帳號都是「這次 sanity 專用、確定沒領過」的新帳號，每次重跑都要換新帳號，
  因為這支腳本會實際把配額領掉，同一批帳號不能重複拿來測「應該成功」的案例
"""
import json
import logging
import threading
import time
import sys
import requests
import random

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ============================================================
# CONFIG - 上線前最後確認這裡！
# ============================================================
BASE_URL = "http://10.81.1.88:8084"   # TODO: 確認是否已切換成 production
DEFAULT_IP = "1.1.1.1"

PROMOTION_NORMAL = 4668091                      # 一個正常、有效、有剩餘配額的活動
PROMOTION_NORMAL_RESTRICT1 = 4670101            # 限制活動期間僅領取1次
PROMOTION_OTHER_MERCHANT = 4659094              # 跨商戶活動 ID（測試應被拒絕）
PROMOTION_LIMITED = 4670096                     # 一天僅領取一次
PROMOTION_TOTAL_AMOUNT = 4670102                # 限制活動總次數僅領取1次
PROMOTION_BUDGET_EXHAUSTED = 4670095 
PROMOTION_MEMBER_QUALIFIED = 4668103            # 會員資格不符，應被拒絕

PLAYER_HAPPY_PATH = 242053825           # TODO: 全新帳號，確定沒領過 PROMOTION_NORMAL
PLAYER_DUPLICATE = 242053825            # TODO: 全新帳號
PLAYER_CROSS_MERCHANT = 242053825       # TODO: 全新帳號
PLAYER_LIMIT_TEST = 242053825           # TODO: 全新帳號

# 併發測試用，人數建議 >= 該活動剩餘配額 + 3，且全部是全新帳號
CONCURRENCY_PLAYERS = [
    # TODO: 填入 8~10 個全新、確定沒領過 PROMOTION_NORMAL_RESTRICT1 的帳號
]
CONCURRENCY_PROMOTION = PROMOTION_NORMAL_RESTRICT1
CONCURRENCY_EXPECTED_SUCCESS = None  # TODO: 填入該活動目前實際剩餘配額

TOKEN = '6f656992-ffd0-440c-a1d1-c4fea31a016f'
PROMOTION_NAME = '8787'   # 用來查詢活動列表的名稱關鍵字，實際比對仍以 promotionId 為準
MERCHANT_CODE = 'gi8viet'

# ============================================================
# 以下不用改
# ============================================================
results_log = []


def get_Ticket_transaction_ID(merchant_code: str, customer_id, promotion_id: int):
    """
    查詢玩家名下「還沒核銷」的票券，只回傳屬於指定 promotion_id 的那些，
    避免把玩家帳上其他活動殘留的票券一起核銷掉。
    """
    tickets = []
    login_url = "http://10.81.1.20:7001/promo-fe/resources/ticket/list"
    params = {"status": "AVAILABLE", "isAll": "N"}
    headers = {
        'Content-Type': 'application/json',
        'Merchant': merchant_code,
        'Language': "CN",
        'CustomerId': str(customer_id),
    }

    response = requests.get(login_url, headers=headers, params=params, verify=False)
    response_json = response.json()

    if not response_json.get('success'):
        logging.error(f"交易ID查詢失敗: {response_json}")
        return tickets

    for item in response_json.get('value', []):
        trans_id = item.get('transactionId')
        item_promotion_id = item.get('promotionId')  # 用不同名字接，避免蓋掉傳入的 promotion_id 參數
        if trans_id and item_promotion_id == promotion_id:
            tickets.append(trans_id)

    logging.info(f"總共可領 {len(tickets)} 張（promotion_id={promotion_id}）")
    return tickets


def approve_to_receive_ticket(trans_id: str, customer_id) -> float:
    """核銷票券，回傳實際領到的金額。查詢失敗或例外時回傳 0，不讓呼叫端因此中斷。"""
    login_url = "http://10.81.1.20:7001/promo-fe/resources/ticket/claim"
    customer_ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    headers = {
        'Content-Type': 'application/json',
        'Merchant': MERCHANT_CODE,
        'Connection': 'keep-alive',
        'Language': 'CN',
        'CustomerId': str(customer_id),
        "CustomerIP": customer_ip,
    }
    payload = {"transactionId": trans_id, "isApp": "N"}

    try:
        response = requests.post(login_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        response_json = response.json()
    except Exception as e:
        logging.error(f"核銷票券發生例外: {e}")
        return 0

    if not response_json.get('success'):
        logging.error(f"領取票券失敗: {response_json}")
        return 0

    value = response_json.get('value', {}).get('value') or 0
    logging.info(f"成功領取票券 交易ID: {trans_id} 金額 {value}")
    return value


def _claim(customer_id: str, promotion_id: int, timeout: int = 10) -> dict:
    headers = {
        "accept": "application/json",
        "CustomerIP": DEFAULT_IP,
        "CustomerId": str(customer_id),
        "Content-Type": "application/json",
    }
    payload = {"promotionId": promotion_id}
    t0 = time.time()
    try:
        resp = requests.post(
            f"{BASE_URL}/promo-fe/resources/tg_raffle/claim",
            headers=headers, json=payload, timeout=timeout,
        )
        return {
            "status_code": resp.status_code,
            "elapsed_ms": round((time.time() - t0) * 1000, 1),
            "body": resp.text,
        }
    except Exception as e:
        return {"status_code": "ERROR", "elapsed_ms": None, "body": str(e)}


def get_promotion_detail(promotion_id: int):
    """
    依名稱查詢活動列表，但用 promotion_id 精準比對出「我真正要的那一筆」，
    避免同名稱底下有多筆活動時，誤抓到列表第一筆導致查到的活動跟實際 claim 的活動對不上。
    回傳 (totalClaimedCount, remainingClaimCount, remainingBudget)，查無資料時回傳 (None, None, None)。
    """
    url = (
        f'http://10.81.1.88:8083/promo-be/resources/promotion/tg_raffle/list'
        f'?name={PROMOTION_NAME}&promoStatus=A&page=1&size=10'
    )
    headers = {
        "accept": "application/json",
        "merchantCode": MERCHANT_CODE,
        "Authorization": TOKEN,
    }
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code != 200:
        logging.error(f"查詢活動列表失敗 status={response.status_code}, body={response.text[:200]}")
        return None, None, None

    response_json = response.json()
    item_list = response_json.get("value", {}).get("list", [])

    for item in item_list:
        if item.get("promotionId") == promotion_id:
            total_claimed = item.get("totalClaimedCount")
            remaining_claim = item.get("remainingClaimCount")
            remaining_budget = item.get("remainingBudget")
            print(
                f"[promotion_id={promotion_id}] totalClaimedCount: {total_claimed}, "
                f"remainingClaimCount: {remaining_claim}, remainingBudget: {remaining_budget}"
            )
            return total_claimed, remaining_claim, remaining_budget

    logging.error(f"在名稱「{PROMOTION_NAME}」的搜尋結果裡，找不到 promotion_id={promotion_id}")
    return None, None, None


def _is_success(result: dict) -> bool:
    if result["status_code"] != 200:
        return False
    try:
        body = json.loads(result["body"])
        return body.get("success") is True or body.get("code") == 0
    except Exception:
        return False


def _check(name: str, condition: bool, detail: str = ""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}  {name}")
    if detail and not condition:
        print(f"        └─ {detail}")
    results_log.append((name, condition))


def check_1_happy_path():
    print("\n[1] 正常玩家領取應成功")

    before_total, before_remaining, before_budget = get_promotion_detail(PROMOTION_NORMAL)
    if before_total is None:
        _check("查詢領取前活動狀態", False, "查無此活動，請確認 PROMOTION_NORMAL 是否正確")
        return

    r = _claim(PLAYER_HAPPY_PATH, PROMOTION_NORMAL)
    _check("claim API 應回傳成功", _is_success(r), f"回應: {r['body'][:200]}")

    ticket = get_Ticket_transaction_ID(MERCHANT_CODE, PLAYER_HAPPY_PATH, PROMOTION_NORMAL)

    value = 0  # 預設值，避免查無票券時後面的比對直接拋例外中斷腳本
    if ticket:
        for trans_id in ticket:
            value = approve_to_receive_ticket(trans_id, PLAYER_HAPPY_PATH)
    else:
        _check("查詢票券", False, "claim 成功但查無可核銷票券，請確認查詢時間點或票券同步是否有延遲")

    after_total, after_remaining, after_budget = get_promotion_detail(PROMOTION_NORMAL)
    if after_total is None:
        _check("查詢領取後活動狀態", False, "查無此活動")
        return

    _check(
        "totalClaimedCount 應 +1",
        after_total == before_total + 1,
        f"實際: {after_total}，原本: {before_total}"
    )
    _check(
        "remainingClaimCount 應 -1",
        after_remaining == before_remaining - 1,
        f"實際: {after_remaining}，原本: {before_remaining}"
    )
    _check(
        f"remainingBudget 應減少 {value}",
        after_budget == before_budget - value,
        f"實際: {after_budget}，原本: {before_budget}"
    )


def check_2_cross_merchant_rejected():
    print("\n[2] 跨商戶活動應被拒絕")
    if PROMOTION_OTHER_MERCHANT == 0:
        print("        ⚠️  SKIP - PROMOTION_OTHER_MERCHANT 未設定")
        return
    r = _claim(PLAYER_CROSS_MERCHANT, PROMOTION_OTHER_MERCHANT)
    ok = (not _is_success(r)) and ("promotion_not_found" in r["body"] or r["status_code"] >= 400)
    _check("跨商戶活動應被拒絕", ok, f"回應: {r['body'][:200]}")


def check_3_duplicate_claim_rejected():
    print("\n[3] 限制玩家領取1次超過應被拒絕（防刷核心邏輯）")
    first = _claim(PLAYER_DUPLICATE, PROMOTION_NORMAL_RESTRICT1)
    second = _claim(PLAYER_DUPLICATE, PROMOTION_NORMAL_RESTRICT1)
    _check("第一次領取應成功", _is_success(first), f"回應: {first['body'][:200]}")
    _check("限制玩家領取1次超過應被拒絕", not _is_success(second), f"回應: {second['body'][:200]}")


def check_4_dailyLimit_exhausted_rejected():
    print("\n[4] 一天僅領取一次的活動應正確拒絕")
    first = _claim(PLAYER_LIMIT_TEST, PROMOTION_LIMITED)
    second = _claim(PLAYER_LIMIT_TEST, PROMOTION_LIMITED)
    _check("第一次領取應成功", _is_success(first), f"回應: {first['body'][:200]}")
    _check("限制玩家領取1次超過應被拒絕", not _is_success(second), f"回應: {second['body'][:200]}")


def check_4_TotalLimit_exhausted_rejected():
    print("\n[4] 總次數限制的活動應正確拒絕")
    first = _claim(PLAYER_LIMIT_TEST, PROMOTION_TOTAL_AMOUNT)
    second = _claim(PLAYER_LIMIT_TEST, PROMOTION_TOTAL_AMOUNT)
    _check("第一次領取應成功", _is_success(first), f"回應: {first['body'][:200]}")
    _check("總次數限制的活動應正確拒絕", not _is_success(second), f"回應: {second['body'][:200]}")


def check_4_BudgetLimit_exhausted_rejected():
    print("\n[4] 預算耗盡的活動應正確拒絕")
    r = _claim(PLAYER_CROSS_MERCHANT, PROMOTION_BUDGET_EXHAUSTED)
    ok = (not _is_success(r)) and ("tg_raffle_inactive" in r["body"] or r["status_code"] >= 400)
    _check("預算耗盡的活動應正確拒絕", ok, f"回應: {r['body'][:200]}")


def check_5_concurrency_no_overissue():
    print("\n[5] 併發搶紅包不超發（重點案例）")
    if not CONCURRENCY_PLAYERS or CONCURRENCY_EXPECTED_SUCCESS is None:
        print("        ⚠️  SKIP - CONCURRENCY_PLAYERS 或 CONCURRENCY_EXPECTED_SUCCESS 未設定")
        return

    n = len(CONCURRENCY_PLAYERS)
    barrier = threading.Barrier(n)
    results = [None] * n

    def worker(idx, cid):
        headers = {
            "accept": "application/json",
            "CustomerIP": DEFAULT_IP,
            "CustomerId": str(cid),
            "Content-Type": "application/json",
        }
        payload = {"promotionId": CONCURRENCY_PROMOTION}
        barrier.wait()
        try:
            resp = requests.post(
                f"{BASE_URL}/promo-fe/resources/tg_raffle/claim",
                headers=headers, json=payload, timeout=10,
            )
            results[idx] = {"status_code": resp.status_code, "body": resp.text}
        except Exception as e:
            results[idx] = {"status_code": "ERROR", "body": str(e)}

    threads = [threading.Thread(target=worker, args=(i, cid)) for i, cid in enumerate(CONCURRENCY_PLAYERS)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success_count = sum(1 for r in results if _is_success(r))
    _check(
        f"{n} 人同時搶，預期成功 {CONCURRENCY_EXPECTED_SUCCESS} 人",
        success_count == CONCURRENCY_EXPECTED_SUCCESS,
        f"實際成功 {success_count} 人（若 > 預期，代表超發，請立即通知後端）"
    )
def check_6_memberQualified_rejected():
    print("\n[6] 會員資格不符的活動應正確拒絕")
    r = _claim(PLAYER_HAPPY_PATH, PROMOTION_MEMBER_QUALIFIED)
    ok = (not _is_success(r)) and ("tg_raffle_inactive" in r["body"] or r["status_code"] >= 400)
    _check("會員資格不符的活動應正確拒絕", ok, f"回應: {r['body'][:200]}")

def main():
    print("=" * 60)
    print("TG 紅包雨 - 上線後 Sanity Check")
    print(f"目標環境: {BASE_URL}")
    print("=" * 60)

    check_1_happy_path()
    check_2_cross_merchant_rejected()
    check_3_duplicate_claim_rejected()
    check_4_dailyLimit_exhausted_rejected()
    check_4_TotalLimit_exhausted_rejected()
    check_4_BudgetLimit_exhausted_rejected()
    check_6_memberQualified_rejected()
    #check_5_concurrency_no_overissue()

    print("\n" + "=" * 60)
    passed = sum(1 for _, ok in results_log if ok)
    total = len(results_log)
    print(f"結果: {passed}/{total} 通過")
    if passed < total:
        print("❌ 有案例失敗，請確認後再放行")
        sys.exit(1)
    else:
        print("✅ 全數通過")
        sys.exit(0)


if __name__ == "__main__":
    main()