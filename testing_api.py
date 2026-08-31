import threading

from flask import logging
import requests
import concurrent.futures
import json
import time

URL = 'http://10.81.1.88:8084/promo-fe/resources/tg_raffle/claim'
PROMOTION_ID = 4670109

# 10 個不同玩家的 CustomerId（請替換成你測試環境中真實存在、
# 且尚未領取過此 promotion 的 10 個帳號）
CUSTOMER_IDS = [
    '242053825', '242142891', '242059822', '242059800', '243666554','244383277', '242059912', '244396210','244382236'
]
barrier = threading.Barrier(len(CUSTOMER_IDS))
def claim(customer_id):
    barrier.wait()
    headers = {
        'accept': 'application/json',
        'CustomerIP': '1.1.1.1',
        'CustomerId': customer_id,
        'Content-Type': 'application/json'
    }
    payload = {"promotionId": PROMOTION_ID}
    t0 = time.time()
    try:
        resp = requests.post(URL, headers=headers, json=payload, timeout=10)
        elapsed = time.time() - t0
        return {
            'customer_id': customer_id,
            'status_code': resp.status_code,
            'elapsed_ms': round(elapsed * 1000, 1),
            'body': resp.text
        }
    except Exception as e:
        return {
            'customer_id': customer_id,
            'status_code': 'ERROR',
            'elapsed_ms': None,
            'body': str(e)
        }

print(f"開始併發測試: {len(CUSTOMER_IDS)} 位玩家同時 claim promotionId={PROMOTION_ID}")
print("=" * 80)

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=len(CUSTOMER_IDS)) as executor:
    futures = [executor.submit(claim, cid) for cid in CUSTOMER_IDS]
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

# 依 customer_id 排序輸出，方便對照
results.sort(key=lambda r: r['customer_id'])
for r in results:
    print(f"CustomerId={r['customer_id']:<12} Status={r['status_code']:<6} "
          f"Time={r['elapsed_ms']}ms  Body={r['body'][:200]}")

print("=" * 80)

# ---- 結果統計 ----
# 請依照你的 API 實際回應格式調整「成功」的判斷條件
success_count = 0
fail_count = 0
for r in results:
    try:
        body_json = json.loads(r['body'])
        # 假設成功時 code == 0 或 200，依實際 API 回應格式修改
        if r['status_code'] == 200 and (
            body_json.get('code') == 0 or body_json.get('success') is True
        ):
            success_count += 1
        else:
            fail_count += 1
            logging.error(f"CustomerId={r['customer_id']} claim failed: {r['body']}")
    except Exception:
        fail_count += 1

print(f"\n成功領取: {success_count} 次")
print(f"失敗/拒絕: {fail_count} 次")
print(f"剩餘配額: 5")

if success_count <= 1:
    print(f"✅ PASS - 成功數 {success_count} ≤ 1，未超發")
else:
    print(f"❌ FAIL - 成功數 {success_count} > 2，發生超發！有併發漏洞")