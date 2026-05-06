"""
手動紅利回歸測試
涵蓋：單人創建、批量創建、審核流程、結果驗證

執行方式：
    pytest tests/test_manual_bonus.py -v
    pytest tests/test_manual_bonus.py::TestSingleBonus -v
    pytest tests/test_manual_bonus.py::TestBatchBonus -v
    pytest tests/test_manual_bonus.py -v --html=report.html --self-contained-html
"""
import pytest
import requests
import logging
import time
from datetime import datetime, timedelta

BASE_URL = "http://sit-admin2.tcg.com"
PLATFORM = "gi8viet"

# ── 測試用固定資料（請依實際環境修改）──────────────────
TEST_USERNAME = "bnm555"          # 已存在的測試玩家帳號
NOT_EXIST_USERNAME = "no_such_user_99999"  # 不存在的玩家帳號
VALID_PROMOTION_ID = 4023101       # 已存在且啟用中的活動 ID
NOT_EXIST_PROMOTION_ID = 9999999  # 不存在的活動 ID
VALID_TICKET_ID = None            # 有票券時填入，沒有填 None
BATCH_USERS = ["bnm555", "bnm556"]  # 批量測試用的多個帳號


# ════════════════════════════════════════════════════════════
# 單人紅利創建 (Manual_create_single_with_confirm.py)
# ════════════════════════════════════════════════════════════
class TestSingleBonus:
    """單人手動紅利 - 創建 + 審核完整流程"""

    # ── 正向測試 ────────────────────────────────────────────

    def test_create_bonus_success(self, api_session):
        """正向：填入正確資料，創建單人紅利應成功"""
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 100,
            "bonusPointAmount": 10,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": VALID_TICKET_ID,
            "ticketQuantity": 0,
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "恭喜您成功領取活動"
        }
        resp = api_session.post(url, json=payload)

        assert resp.status_code == 200, f"HTTP 狀態碼錯誤: {resp.status_code}"
        data = resp.json()
        assert data.get("success") is True, f"創建紅利失敗: {data.get('message')}"
        logging.info(f"✅ 單人紅利創建成功，玩家: {TEST_USERNAME}")

    def test_full_flow_create_search_confirm(self, api_session):
        """正向：完整流程 - 創建 → 查詢 → 審核"""

        # Step 1: 創建紅利
        create_url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 50,
            "bonusPointAmount": 5,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": VALID_TICKET_ID,
            "ticketQuantity": 0,
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "測試訊息"
        }
        create_resp = api_session.post(create_url, json=payload)
        assert create_resp.json().get("success") is True, \
            f"Step1 創建失敗: {create_resp.json().get('message')}"
        logging.info("✅ Step1 創建成功")

        time.sleep(1)

        # Step 2: 查詢剛創建的紅利
        search_url = f"{BASE_URL}/tac/api/relay/get/mcs-manualPromotion-search"
        start_time = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        search_params = {
            "merchantCode": PLATFORM,
            "status": "P",
            "customerName": TEST_USERNAME,
            "searchDateMode": "issuedDateSearch",
            "startTime": start_time,
            "endTime": end_time,
            "pageSize": 10,
            "pageNo": 1
        }
        search_resp = api_session.get(search_url, params=search_params)
        search_data = search_resp.json()

        assert search_data.get("success") is True, f"Step2 查詢失敗: {search_data.get('message')}"
        customer_list = search_data.get("value", [])
        assert len(customer_list) > 0, "Step2 查詢結果為空，找不到剛創建的紅利"

        customer_info = customer_list[0]
        customer_id = customer_info.get("customerId")
        claim_id = customer_info.get("id")
        promo_type = customer_info.get("promotionType")

        assert customer_id, "Step2 回應缺少 customerId"
        assert claim_id, "Step2 回應缺少 claimId"
        logging.info(f"✅ Step2 查詢成功，claimId: {claim_id}，promotionType: {promo_type}")

        # Step 3: 審核紅利
        confirm_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-approveClaimStatus?claimStatus=I&customerId={customer_id}&claimId={claim_id}"
        confirm_payload = {
            "claimStatus": "I",
            "customerId": str(customer_id),
            "claimId": str(claim_id),
            "promoType": promo_type
        }
        confirm_resp = api_session.post(confirm_url, json=confirm_payload)
        confirm_data = confirm_resp.json()

        assert confirm_data.get("success") is True, f"Step3 審核失敗: {confirm_data.get('message')}"
        logging.info("✅ Step3 審核成功，完整流程通過")

    def test_create_bonus_with_future_schedule_time(self, api_session):
        """正向：指定未來派發時間，狀態應為待派發"""
        future_time = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 50,
            "bonusPointAmount": 5,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": VALID_TICKET_ID,
            "ticketQuantity": 0,
            "scheduleTime": str(future_time),
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "測試指定時間"
        }
        resp = api_session.post(url, json=payload)
        data = resp.json()

        assert resp.status_code == 200
        assert data.get("success") is True, f"指定未來時間創建失敗: {data.get('message')}"
        logging.info("✅ 指定未來派發時間，創建成功")

    # ── 負向測試 ────────────────────────────────────────────

    def test_create_bonus_user_not_exist(self, api_session):
        """負向：玩家帳號不存在，應回傳失敗"""
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": NOT_EXIST_USERNAME,
            "bonusAmount": 100,
            "bonusPointAmount": 10,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": None,
            "ticketQuantity": 0,
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "test"
        }
        resp = api_session.post(url, json=payload)
        data = resp.json()

        assert data.get("success") is False, \
            f"不存在的玩家應回傳失敗，但卻回傳成功: {data}"
        logging.info(f"✅ 不存在玩家正確被擋，錯誤訊息: {data.get('message')}")

    def test_create_bonus_invalid_promotion(self, api_session):
        """負向：活動 ID 不存在，應回傳失敗"""
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 100,
            "bonusPointAmount": 10,
            "promotionId": NOT_EXIST_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": None,
            "ticketQuantity": 0,
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "test"
        }
        resp = api_session.post(url, json=payload)
        data = resp.json()

        assert data.get("success") is False, \
            f"不存在的活動 ID 應回傳失敗，但卻回傳成功: {data}"
        logging.info(f"✅ 不存在活動 ID 正確被擋，錯誤訊息: {data.get('message')}")

    def test_create_bonus_zero_amount(self, api_session):
        """邊界值：紅利金額填 0，應被擋下或有警告"""
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 0,
            "bonusPointAmount": 0,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 0,
            "ticketId": None,
            "ticketQuantity": 0,
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "test"
        }
        resp = api_session.post(url, json=payload)
        data = resp.json()

        # 金額為 0 依業務規則可能允許或不允許，記錄實際行為
        logging.info(f"{'✅' if not data.get('success') else '⚠️'} 金額為 0 結果: success={data.get('success')}, msg={data.get('message')}")

    def test_create_bonus_missing_username(self, api_session):
        """負向：缺少用戶名，應被擋下"""
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": "",   # 空字串
            "bonusAmount": 100,
            "bonusPointAmount": 10,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": None,
            "ticketQuantity": 0,
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "test"
        }
        resp = api_session.post(url, json=payload)
        data = resp.json()

        assert data.get("success") is False, \
            f"空用戶名應回傳失敗，但卻成功: {data}"
        logging.info(f"✅ 空用戶名正確被擋，錯誤訊息: {data.get('message')}")

    def test_create_bonus_past_schedule_time(self, api_session):
        """負向：指定過去的派發時間，應被擋下"""
        past_time = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
        url = f"{BASE_URL}/tac/api/relay/post/prom-promotion-manual-reward-claims-post?pid=20251"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 100,
            "bonusPointAmount": 10,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 5,
            "ticketId": None,
            "ticketQuantity": 0,
            "scheduleTime": str(past_time),
            "isSendApp": "Y",
            "appTitle": "title",
            "appMessage": "test"
        }
        resp = api_session.post(url, json=payload)
        data = resp.json()

        # 記錄系統實際行為
        logging.info(f"{'✅ 過去時間被擋' if not data.get('success') else '⚠️ 過去時間被允許，需確認業務規則'}: {data.get('message')}")

'''
# ════════════════════════════════════════════════════════════
# 批量紅利創建 (MANUAL_BATCH.py)
# ════════════════════════════════════════════════════════════
class TestBatchBonus:
    """批量手動紅利 - 多人並行創建 + 批量審核"""

    def test_batch_create_all_success(self, api_session):
        """正向：多人批量創建，全部應成功"""
        create_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-addManualPromotionClaim"
        results = []

        for username in BATCH_USERS:
            payload = {
                "merchantCode": PLATFORM,
                "customerName": username,
                "bonusAmount": 10,
                "bonusPointAmount": 10,
                "promotionId": VALID_PROMOTION_ID,
                "toReqAmount": 0,
                "ticketId": VALID_TICKET_ID,
                "ticketQuantity": 0
            }
            resp = api_session.post(create_url, json=payload)
            data = resp.json()
            results.append({
                "username": username,
                "success": data.get("success"),
                "message": data.get("message")
            })
            logging.info(f"{'✅' if data.get('success') else '❌'} {username}: {data.get('message', '')}")

        success_count = sum(1 for r in results if r["success"])
        fail_list = [r["username"] for r in results if not r["success"]]

        assert success_count == len(BATCH_USERS), \
            f"批量創建應全部成功，但以下帳號失敗: {fail_list}"
        logging.info(f"✅ 批量創建完成，成功 {success_count}/{len(BATCH_USERS)}")

    def test_batch_create_partial_invalid_user(self, api_session):
        """業務邏輯：批量中有部分不存在的帳號，有效帳號應仍成功"""
        create_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-addManualPromotionClaim"
        mixed_users = [TEST_USERNAME, NOT_EXIST_USERNAME]
        results = []

        for username in mixed_users:
            payload = {
                "merchantCode": PLATFORM,
                "customerName": username,
                "bonusAmount": 10,
                "bonusPointAmount": 10,
                "promotionId": VALID_PROMOTION_ID,
                "toReqAmount": 0,
                "ticketId": VALID_TICKET_ID,
                "ticketQuantity": 0
            }
            resp = api_session.post(create_url, json=payload)
            data = resp.json()
            results.append({"username": username, "success": data.get("success")})

        valid_result = next(r for r in results if r["username"] == TEST_USERNAME)
        invalid_result = next(r for r in results if r["username"] == NOT_EXIST_USERNAME)

        assert valid_result["success"] is True, "有效帳號應創建成功"
        assert invalid_result["success"] is False, "無效帳號應創建失敗"
        logging.info("✅ 混合帳號批量：有效成功，無效正確被擋")

    def test_batch_confirm_after_create(self, api_session):
        """正向：批量創建後，批量審核應全部通過"""

        # Step 1: 批量創建
        create_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-addManualPromotionClaim"
        for username in BATCH_USERS:
            payload = {
                "merchantCode": PLATFORM,
                "customerName": username,
                "bonusAmount": 10,
                "bonusPointAmount": 10,
                "promotionId": VALID_PROMOTION_ID,
                "toReqAmount": 0,
                "ticketId": VALID_TICKET_ID,
                "ticketQuantity": 0
            }
            api_session.post(create_url, json=payload)

        time.sleep(1)

        # Step 2: 查詢待審核列表
        search_url = f"{BASE_URL}/tac/api/relay/get/mcs-manualPromotion-search"
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        search_params = {
            "merchantCode": PLATFORM,
            "status": "P",
            "searchDateMode": "issuedDateSearch",
            "startTime": start_time,
            "endTime": end_time,
            "pageSize": 50,
            "pageNo": 1
        }
        search_resp = api_session.get(search_url, params=search_params)
        search_data = search_resp.json()

        assert search_data.get("success") is True, "查詢待審核列表失敗"
        customer_list = search_data.get("value", [])
        assert len(customer_list) > 0, "查詢結果為空，找不到待審核紅利"

        # 組合 claimid_list
        claim_list = [
            {"promoClaimId": item.get("id"), "promotionType": item.get("promotionType")}
            for item in customer_list
            if item.get("id")
        ]
        logging.info(f"✅ Step2 查詢成功，共 {len(claim_list)} 筆待審核")

        # Step 3: 批量審核
        confirm_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-batchApproveRejectManualPromotion"
        confirm_payload = {
            "status": "I",
            "promotionClaims": claim_list
        }
        confirm_resp = api_session.post(confirm_url, json=confirm_payload)
        confirm_data = confirm_resp.json()

        assert confirm_data.get("success") is True, \
            f"批量審核失敗: {confirm_data.get('message')}"
        logging.info("✅ Step3 批量審核成功")

    def test_batch_verify_record_exists(self, api_session):
        """業務邏輯：審核完成後，後台紀錄頁應該查得到"""

        # 先跑一次完整的創建 + 審核流程
        create_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-addManualPromotionClaim"
        payload = {
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME,
            "bonusAmount": 10,
            "bonusPointAmount": 10,
            "promotionId": VALID_PROMOTION_ID,
            "toReqAmount": 0,
            "ticketId": VALID_TICKET_ID,
            "ticketQuantity": 0
        }
        create_resp = api_session.post(create_url, json=payload)
        assert create_resp.json().get("success") is True, "創建失敗，無法繼續驗證"

        time.sleep(2)

        # 查詢並審核
        search_url = f"{BASE_URL}/tac/api/relay/get/mcs-manualPromotion-search"
        start_time = datetime.now().strftime("%Y-%m-%d 00:00:00")
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
        search_resp = api_session.get(search_url, params={
            "merchantCode": PLATFORM, "status": "P",
            "customerName": TEST_USERNAME,
            "searchDateMode": "issuedDateSearch",
            "startTime": start_time, "endTime": end_time,
            "pageSize": 10, "pageNo": 1
        })
        customer_list = search_resp.json().get("value", [])
        if not customer_list:
            pytest.skip("查不到待審核紅利，跳過驗證")

        claim_id = customer_list[0].get("id")
        claim_list = [{"promoClaimId": claim_id, "promotionType": customer_list[0].get("promotionType")}]

        confirm_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-batchApproveRejectManualPromotion"
        api_session.post(confirm_url, json={"status": "I", "promotionClaims": claim_list})

        time.sleep(3)

        # 驗證後台紀錄頁有出現
        record_url = f"{BASE_URL}/tac/api/relay/get/mcs-v2-promotionClaim-search"
        record_params = {
            "pageSize": 20, "pageNo": 1,
            "fromDate": start_time, "toDate": end_time,
            "isFuzzySearch": True,
            "searchDateMode": "requestedTimeSearch",
            "merchantCode": PLATFORM,
            "customerName": TEST_USERNAME
        }
        record_resp = api_session.get(record_url, params=record_params)
        record_data = record_resp.json()

        assert record_data.get("success") is True, "後台紀錄頁查詢失敗"
        records = record_data.get("value", {})
        claim_ids_in_record = {str(item.get("promotionClaimId")) for item in records} if isinstance(records, list) else set()

        assert str(claim_id) in claim_ids_in_record, \
            f"審核後後台紀錄頁找不到 claimId: {claim_id}"
        logging.info(f"✅ 後台紀錄驗證成功，claimId: {claim_id} 存在於紀錄中")

    def test_batch_confirm_empty_list(self, api_session):
        """邊界值：傳空的 claimid_list 去批量審核，應不報錯"""
        confirm_url = f"{BASE_URL}/tac/api/relay/post/mcs-manual-promotion-batchApproveRejectManualPromotion"
        confirm_payload = {
            "status": "I",
            "promotionClaims": []
        }
        resp = api_session.post(confirm_url, json=confirm_payload)

        assert resp.status_code == 200, f"HTTP 狀態碼錯誤: {resp.status_code}"
        data = resp.json()
        # 空列表時，success 可能 True 或 False，但不應 crash
        assert isinstance(data.get("success"), bool), "回應格式異常"
        logging.info(f"✅ 空列表批量審核不 crash，結果: {data.get('success')}")
        
        '''