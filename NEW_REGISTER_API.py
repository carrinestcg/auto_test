import requests
import logging
from DB_connect import DB_connect
import Customer_id 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def get_token():
    try:
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
        token_data=requests_data.json()
        return token_data.get("token")
    
    except Exception as e:
        logging.error(f"拿取token發生異常{e}")

def header(token,MerchantCode):
    return {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Content-Type": "application/json",
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Merchant": MerchantCode,
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/20200",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "merchantCode": MerchantCode,
    "platform": "TCG"
    }
def _humanize_create_agent_error(message: str, platform: str) -> str:
    text = message or "未知錯誤"
    lower = text.lower()
    if "rebate value not in range" in lower:
        return f"平台 {platform} 的返點設定超出允許範圍，請聯絡管理員更新 rebate configs"
    return text


def _classify_create_agent_error(message: str) -> str:
    text = message or ""
    lower = text.lower()
    exists_keywords = (
        "exist",
        "already",
        "duplicate",
        "重複",
        "已存在",
        "已经存在",
        "已被使用",
        "已被註冊",
        "已被注册",
    )
    if any(keyword in lower or keyword in text for keyword in exists_keywords):
        return "exists"
    return "error"


def create_agent(token, player: str, platform: str):

    API_URL = "http://sit-admin2.tcg.com/mcs_console/api/agentInfo/createAgent" 
    params={
        "agentName": player,
        "masterAgentType":2,
    }
    
    config_map = {
        "gi8viet": [
            {"type": "LIVE", "rebateValue": 2, "rebateSubordinateLimit": 2},
            {"type": "RNG", "rebateValue": 2, "rebateSubordinateLimit": 2},
            {"type": "VIETNAM_LOTTO", "rebateValue": 99, "rebateSubordinateLimit": 99},
            {"type": "FISH", "rebateValue": 1.5, "rebateSubordinateLimit": 1.5},
            {"type": "ELOTTO", "rebateValue": 1980, "rebateSubordinateLimit": 1980}
        ],
        "huamei": [
            {"type": "PVP", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "LIVE", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "RNG", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "11X5_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "K3_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "LHC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "PK10_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "SSC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "SSC_3-50", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "BBIN", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "IBC", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "SPORTS-PARLAY", "rebateValue": 0, "rebateSubordinateLimit": 0},
            {"type": "FISH", "rebateValue": 1, "rebateSubordinateLimit": 1},
        ],
        "tcgdemov3": [
            {"type": "LIVE", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "11X5_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "11X5_1-102", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "K3_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "LF_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "LHC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "PCB_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "PK10_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "SSC_1", "rebateValue": 1980, "rebateSubordinateLimit": 1980},
            {"type": "ELOTTO", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "SEA_LOTT", "rebateValue": 100, "rebateSubordinateLimit": 100}
        ],
        "rollbet": [
            {"type": "PVP", "rebateValue": 900, "rebateSubordinateLimit": 900},
            {"type": "RNG", "rebateValue": 2, "rebateSubordinateLimit": 2},
            {"type": "VIETNAM_LOTTO", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "FISH", "rebateValue": 800, "rebateSubordinateLimit": 800}
        ],
        "lodibet": [
            {"type": "LIVE", "rebateValue": 100, "rebateSubordinateLimit": 100},
            {"type": "ELOTTO", "rebateValue": 1, "rebateSubordinateLimit": 1},
            {"type": "SEA_LOTT", "rebateValue": 30, "rebateSubordinateLimit": 30}
        ]
    }
    payload = {
    "merchantCode": platform,
    "agentName": player,
    "configs":config_map.get(platform,[])
    }

    headers = header(token,platform)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.post(API_URL, params=params,json=payload, headers=headers, cookies=cookies, verify=False)
        response.raise_for_status()
        
        
        response_data = response.json()
        logging.info(response.text)

        
        if response_data.get("success"):
            logging.info(f"新建代理玩家成功: {player}")
            return {
                "success": True,
                "reason": "ok",
                "message": f"新建代理玩家成功: {player}",
                "merchant_code": platform,
            }

        error_msg = _humanize_create_agent_error(
            response_data.get("message", "未知錯誤"),
            platform,
        )
        reason = _classify_create_agent_error(error_msg)
        if reason == "exists":
            logging.error(f"帳號已存在: {player}（{error_msg}）")
            return {
                "success": False,
                "reason": "exists",
                "message": error_msg,
                "merchant_code": None,
            }

        logging.error(f"創建代理失敗: {error_msg}")
        return {
            "success": False,
            "reason": "error",
            "message": error_msg,
            "merchant_code": None,
        }

    except requests.RequestException as e:
        logging.error(f"HTTP錯誤 {e}")
        return {
            "success": False,
            "reason": "error",
            "message": str(e),
            "merchant_code": None,
        }
    except ValueError as e:
        logging.error(f"JSON解析錯誤: {e}")
        return {
            "success": False,
            "reason": "error",
            "message": str(e),
            "merchant_code": None,
        }
    except Exception as e:
        logging.error(f"其他錯誤: {e}")
        return {
            "success": False,
            "reason": "error",
            "message": str(e),
            "merchant_code": None,
        }
    
def reset_to_123qwe(customerId:int,merchantCode):
    URL="http://10.81.1.22:7001/tcg-uss-ae/password"
    headers={
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        "Accept":"application/json"
    }
    if merchantCode == 'tcgdemov3':
        payload={ 
            "customerId": customerId, 
            "needLogInToChangePassword": True, 
            "password": "qwe123" 
    }
    else:
        payload={ 
            "customerId": customerId, 
            "needLogInToChangePassword": True, 
            "password": "123qwe" 
    }
    response=requests.put(URL,headers=headers,json=payload,verify=False)
    response_data=response.json()
    if response_data.get("success"):
        logging.info("修改密碼成功")
        return True
    else:
        return logging.info("修改密碼失敗")

def _build_create_player_message(details):
    if not details:
        return "創建玩家失敗"

    exists_items = [item for item in details if item.get("status") == "exists"]
    failed_items = [item for item in details if item.get("status") == "failed"]
    created_items = [item for item in details if item.get("status") in ("created", "password_failed")]

    if exists_items and not created_items and not failed_items:
        if len(exists_items) == 1:
            return exists_items[0].get("message") or "帳號已存在"
        names = "、".join(item.get("username", "") for item in exists_items if item.get("username"))
        return f"以下帳號已存在：{names}"

    if created_items and not exists_items and not failed_items:
        if len(created_items) == 1:
            item = created_items[0]
            if item.get("status") == "password_failed":
                return f"帳號 {item.get('username')} 創建成功，但重設密碼失敗"
            return f"帳號 {item.get('username')} 創建成功並已重設密碼"
        return f"成功創建 {len(created_items)} 個帳號"

    parts = []
    if created_items:
        parts.append(f"成功 {len(created_items)} 筆")
    if exists_items:
        parts.append(f"已存在 {len(exists_items)} 筆")
    if failed_items:
        parts.append(f"失敗 {len(failed_items)} 筆")
    return "創建結果：" + "，".join(parts)


def main(merchant_code, username_list):
    try:
        token = get_token()
        print("取得的 token:", token)
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)
        return {
            "result_code": 0,
            "customer_id": None,
            "message": f"啟動時取得 token 發生錯誤: {e}",
            "details": [],
        }

    if not token:
        logging.error("無法取得後台 token")
        return {
            "result_code": 0,
            "customer_id": None,
            "message": "無法取得後台 token",
            "details": [],
        }

    procedure_type = 0
    customer_id = None
    details = []
    print(username_list)

    for username in username_list:
        customer_name = f"{merchant_code}@{username}"
        existing_id = Customer_id.main(username, merchant_code, query_type=1)
        if existing_id:
            message = f"帳號 {username} 已存在（{customer_name}）"
            logging.warning(message + f"，customer_id={existing_id}")
            details.append({
                "username": username,
                "status": "exists",
                "customer_id": existing_id,
                "message": message,
            })
            continue

        created = create_agent(token, username, merchant_code)
        if not created.get("success"):
            reason = created.get("reason", "error")
            status = "exists" if reason == "exists" else "failed"
            if status == "exists":
                message = f"帳號 {username} 已存在：{created.get('message', '代理帳號重複')}"
            else:
                message = f"帳號 {username} 創建失敗：{created.get('message', '未知錯誤')}"
            logging.error(message)
            details.append({
                "username": username,
                "status": status,
                "message": message,
            })
            continue

        customer_id = Customer_id.main(username, merchant_code, query_type=1)
        print(customer_id)

        if customer_id:
            if reset_to_123qwe(customer_id, merchant_code):
                procedure_type = 1
                details.append({
                    "username": username,
                    "status": "created",
                    "customer_id": customer_id,
                    "message": f"帳號 {username} 創建成功並已重設密碼",
                })
            else:
                procedure_type = 2
                details.append({
                    "username": username,
                    "status": "password_failed",
                    "customer_id": customer_id,
                    "message": f"帳號 {username} 創建成功，但重設密碼失敗",
                })
        else:
            message = f"帳號 {username} 創建後查無 CustomerID（{customer_name}）"
            logging.error("沒有拿到CustomerID")
            details.append({
                "username": username,
                "status": "failed",
                "message": message,
            })

    message = _build_create_player_message(details)
    if procedure_type == 1:
        return {
            "result_code": 1,
            "customer_id": customer_id,
            "message": message,
            "details": details,
        }
    if procedure_type == 2:
        return {
            "result_code": 2,
            "customer_id": customer_id,
            "message": message,
            "details": details,
        }

    only_exists = details and all(item.get("status") == "exists" for item in details)
    return {
        "result_code": -1 if only_exists else 0,
        "customer_id": customer_id,
        "message": message,
        "details": details,
    }

        

   