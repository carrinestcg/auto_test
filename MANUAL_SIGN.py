import requests
import logging
import time
import yaml
import os
import random
import base64
import mimetypes
from pathlib import Path
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Type A 附言報名固定附圖（本機路徑，執行時自動轉 data URL）
DEFAULT_SIGNUP_PICTURE = Path(__file__).resolve().parent / "assets" / "1.png"
DEFAULT_SIGNUP_REMARKS = "testAPI"


def _file_to_data_url(image_path):
    file_path = Path(str(image_path)).expanduser()
    if not file_path.is_file():
        raise FileNotFoundError(f"找不到圖片：{image_path}")

    mime, _ = mimetypes.guess_type(str(file_path))
    if not mime or not mime.startswith("image/"):
        mime = "image/jpeg"

    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def normalize_signup_pictures(picture_inputs=None):
    """

    支援：
    - 本機路徑：/path/to/a.jpg
    - 已是 data URL：data:image/jpeg;base64,...
    - 路徑或 data URL 的 list
    """
    if not picture_inputs:
        return []

    if isinstance(picture_inputs, str):
        text = picture_inputs.strip()
        if not text:
            return []
        if text.startswith("data:image"):
            return [text]
        return [_file_to_data_url(text)]

    pictures = []
    for item in picture_inputs:
        text = str(item or "").strip()
        if not text:
            continue
        if text.startswith("data:image"):
            pictures.append(text)
        else:
            pictures.append(_file_to_data_url(text))
    return pictures


def get_default_signup_pictures():
    return normalize_signup_pictures(str(DEFAULT_SIGNUP_PICTURE))


class Frontend:
    def __init__(self,credential_fe:dict):
        self.session=requests.Session()
        self.username=''
        self.userid=''
        self.credential_fe=credential_fe
        self.token=None
        self.token_expire=None
        self.token=self.get_token_login_frontend(credential_fe['username'],credential_fe['password'])
        self.type=''
    def get_token_login_frontend(self, username, password):
        try:

            if self.token is not None and self.token_expire is not None and datetime.now()<self.token_expire:
                return self.token
            
            login_url='http://sit3.sit-gi8viet.com/wps/session/login/unsecure'
            
            headers = {
                'Content-Type': 'application/json',
                'Merchant': 'gi8viet',
                
            }
            login_data={
                'username':username,
                'password':password
            } 
            self.username=username
            requests_data=self.session.post(login_url,json=login_data,headers=headers, verify=False)
            body = requests_data.json()
            logging.info("前台登入回應: %s", body)
            if not body.get("success"):
                logging.error("前台登入失敗: %s", body.get("message") or body)
                return None
            value = body.get("value") or {}
            self.username = value.get("userName")
            self.userid = value.get("id")
            self.token = value.get("token")
            if not self.token:
                logging.error("前台登入回應缺少 token: %s", body)
                return None
            if not value.get("mobileNum"):
                logging.warning("玩家 %s 的 mobileNum 為空，部分手工報名 API 可能回傳 user_record_not_exists", username)

            self.token_expire=datetime.now()+timedelta(minutes=25)
            return self.token
        
        except requests.RequestException as e:
            logging.error(f"請求失敗{e}")
            return None
    def is_token_valid(self):
        
        return (self.token is not None and 
                self.token_expire is not None and 
                datetime.now() < self.token_expire)
    
    def Join_promotion(self,promo:int,account:str):
        login_URL="http://sit3.sit-gi8viet.com/wps/relay/MCSFE_signUpPromotionJoin"

        headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Content-Type': 'application/json',
                    'Merchant': 'gi8viet',
                    "Authorization":self.token,
                    'Connection': 'keep-alive',
                    'Language': 'EN',
                    'Origin': 'http://sit3.sit-gi8viet.com',
                    'Referer': 'http://sit3.sit-gi8viet.com/promotions',
                    'ModuleId': 'DPSTBAS3',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',  
                   
                }
        payload={
                    "promotionId": int(promo)
                }
        
        response = self.session.post(login_URL, headers=headers, json=payload, verify=False)
        response_json = response.json()
        logging.info("直接報名回應: %s", response_json)
                
        if response_json.get('success'):
                logging.info(f"玩家{account}成功報名")
                return True, response_json

        logging.error(f"玩家{account}直接報名失敗: {response_json}")
        return False, response_json
            
    def Join_promotion_write_note(self, promo: int, account: str, pictures=None):
            login_URL="http://sit3.sit-gi8viet.com/wps/relay/MCSFE_signUpRequestReward"
    
            headers={
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Content-Type': 'application/json',
                        'Merchant': 'gi8viet',
                        "Authorization":self.token,
                        'Connection': 'keep-alive',
                        'Device': 'web',
                        'Language': 'EN',
                        'Origin': 'http://sit3.sit-gi8viet.com',
                        'Referer': 'http://sit3.sit-gi8viet.com/promotions',
                        'ModuleId': 'DPSTBAS3',
                        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                        'x-requested-with': 'XMLHttpRequest',  
                       
                    }
            payload={
                    "pictures": pictures if pictures is not None else get_default_signup_pictures(),
                    "promotionId": int(promo),
                    "remarks": DEFAULT_SIGNUP_REMARKS,
                }
            
            response = self.session.post(login_URL, headers=headers, json=payload, verify=False)
            response_json = response.json()
            logging.info("填寫附言報名回應: %s", response_json)
            if response_json.get('success'):
                    logging.info(f"玩家{account}成功報名（附言）")
                    return True, response_json

            logging.error(f"玩家{account}填寫附言報名失敗: {response_json}")
            return False, response_json
class Backend:
    def header(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": self.token,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Language": "zh_CN",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/24785",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "TCG3",
            "merchantCode": "gi8viet",
            "notPending": "true",
            "platform": "TCG",
        }
    def __init__(self,credential_be:str):
        self.session=requests.Session()
        self.credential_be=credential_be
        self.token_expire=None
        self.type=''
        self.token_backend=self.get_token_backend(credential_be['operatorName'],credential_be['password'])
        self.token=self.token_backend
    def get_token_backend(self,operatorName,password):
        login_url="http://sit-admin2.tcg.com/tac/api/login/password"
        payload={
            "operatorName": operatorName,
            "password": password
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
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
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token
    def get_record_id(self,account:str):
        record_ids = []
        API_URL3="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-signUpList-search-get"
        
        headers=self.header()
        cookies = {
            "language": "zh_CN"
        }

        params={
            "userName": account,
            "promotionName": "",
            "status": "",
            "pageSize": 10,
            "pageNo": 1,
            "merchantCode": "gi8viet",
        }
        try:
            response=requests.get(API_URL3, cookies=cookies,params=params,headers=headers, verify=False)

            response_data=response.json()
            logging.info(f"完整回應: {response_data}")
            if response_data.get("success"):
                record_id_list=response_data.get("value")
                for value in record_id_list:
                    record_id=value.get("recordId")
                    logging.info("拿到recordid")
                    record_ids.append(record_id)
                return record_ids
            else:
                logging.error("沒有拿到recordid: %s", response_data)
                return []
        
        except Exception as e:
            logging.error(f"API呼叫失敗{e}")
            return []
    def get_payload__detail(self,record_id):
        API_URL3="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-signUpList-getCustomerSignUpConfig-get"
        params={
            "recordId": record_id
        }
        headers=self.header()
        response=requests.get(API_URL3, params=params, headers=headers, verify = False)
        response_json=response.json()
        if response_json.get("success"):
            value_dict=response_json.get("value")
            logging.info(value_dict)
            return value_dict
        else:
            logging.error(response_json)
            return None
        
    def Approve_to_send_bounus(self,account:str,promo_id:int,record_id:int, value_dict:dict):
        configId           = value_dict.get("configId")
        bonus_amount        = value_dict.get("bonusAmount")
        point_amount        = value_dict.get("pointAmount")
        ticket_id           = value_dict.get("ticketId")
        min_required_to     = value_dict.get("minRequiredTo")
        turnover_multiplier = value_dict.get("turnoverMultiplier")
        forAllLabel         = value_dict.get("forAllLabel", "Y")
        ticket_name         = value_dict.get("ticketName", None)
        ticket_type         = value_dict.get("ticketType", None)
        ticket_quantity     = value_dict.get("ticketQuantity", None)
        sign_up_labels      = value_dict.get("signUpPromotionConfigLabels", None)
        API_URL3="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-signUpList-approve-create"
        
        headers=self.header()
        cookies = {
            "language": "zh_CN"
        }

        payload={
            "promotionId": promo_id,
            "configId": configId,
            "bonusAmount": bonus_amount,
            "pointAmount": point_amount,
            "turnoverMultiplier": turnover_multiplier,
            "minRequiredTo": min_required_to,
            "forAllLabel": forAllLabel,
            "ticketId": ticket_id,
            "ticketName": ticket_name,
            "ticketType": ticket_type,
            "ticketQuantity": ticket_quantity,
            "signUpPromotionConfigLabels": sign_up_labels,
            "customerName": account,
            "recordId": record_id,
            "turnoverAmount": 0,
            "ticketTotalQuantity": ticket_quantity,
            "bonusBudget": 999555,
            "pointsBudget": 999555
        }
        try:
            response=requests.post(API_URL3, cookies=cookies, json=payload,headers=headers, verify=False)

            response_data=response.json()
            if response_data.get("success"):
                logging.info("派發手工報名活動成功")
                return True  
            else:
                logging.error("派發手工報名活動失敗")
                return False
        
        except Exception as e:
            logging.error(f"API呼叫失敗{e}")
            return False
    
def _format_api_error(response_json):
    if not isinstance(response_json, dict):
        return str(response_json)
    parts = [
        response_json.get("message"),
        response_json.get("errorCode"),
        response_json.get("detail"),
    ]
    text = " · ".join(str(p) for p in parts if p)
    return text or str(response_json)


def main(username, promo_id, type_value, password="123qwe"):
    username = str(username or "").strip()
    type_value = str(type_value or "B").strip().upper()
    try:
        promo_id = int(str(promo_id).strip())
    except (TypeError, ValueError):
        return {"success": False, "message": f"活動 ID 無效：{promo_id}"}

    credential_be = {
            "operatorName": "carrine03",
            "password": "Test@1234"
    }
    credential_fe = {
            "username": username,
            "password": password or "123qwe"
    }

    frontend_ok = False
    frontend_error = None
    try:
        frontend = Frontend(credential_fe)
        if not frontend.token:
            return {"success": False, "message": "前台登入失敗，請確認帳號密碼"}

        if type_value == "B":
            frontend_ok, frontend_resp = frontend.Join_promotion(promo_id, username)
        elif type_value == "A":
            join_ok, join_resp = frontend.Join_promotion(promo_id, username)
            if not join_ok:
                frontend_ok = False
                frontend_resp = join_resp
            else:
                frontend_ok, frontend_resp = frontend.Join_promotion_write_note(
                    promo_id,
                    username,
                )
        else:
            return {"success": False, "message": f"未知 requireType：{type_value}"}

        if not frontend_ok:
            frontend_error = _format_api_error(frontend_resp)
            hint = ""
            if (frontend_resp or {}).get("errorCode") == "user_record_not_exists":
                hint = (
                    "呼叫失敗"
                )
            return {
                "success": False,
                "message": f"前台報名失敗：{frontend_error}{hint}",
                "step": "frontend_join",
                "requireType": type_value,
                "promotion_id": promo_id,
            }

        time.sleep(1.5)
    except Exception as e:
        logging.error(f"前台報名時發生錯誤: {e}")
        return {"success": False, "message": f"前台報名異常：{e}"}

    try:
        backend=Backend(credential_be)    
        if not backend.token:
            return {"success": False, "message": "後台登入失敗，無法審核派彩"}

        record_list = backend.get_record_id(str(username)) or []
        if not record_list:
            return {
                "success": False,
                "message": (
                    f"前台報名已成功，但後台查不到 {username} 的待審記錄。"
                ),
                "step": "backend_search",
            }

        for record in record_list:
            if record:
                value_dict=backend.get_payload__detail(record)
                if not value_dict:
                    continue
                result=backend.Approve_to_send_bounus(str(username), promo_id, record, value_dict)  
                if result:
                    return {
                        "success": True,
                        "message": "手工報名完成（前台報名 + 後台審核）",
                        "requireType": type_value,
                        "promotion_id": promo_id,
                    }

        return {
            "success": False,
            "message": "後台找到報名紀錄，但審核派彩失敗",
            "step": "backend_approve",
        }
    except Exception as e:
        logging.error(f"後台審核時發生錯誤: {e}")
        return {"success": False, "message": f"後台審核異常：{e}"}