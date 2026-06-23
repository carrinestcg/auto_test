import requests
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def schedule_manual_bonus(setting_id, date):
    URL="http://10.81.1.88:8086/promo-rd/manual/promotion/statistics"
    header={
        "accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br"
    }
    params={
        "settingId": setting_id,
        "targetDate" : date
        }
    respone=requests.post(URL,headers=header, params=params, verify=False)
    if respone.status_code==200:
        return True
    else:
        return False
    
def main(setting_id, date):
    
    if setting_id:
        logging.info(f"拿到setting_ID: {setting_id}")
        if schedule_manual_bonus(setting_id, date):
            logging.info(f"成功調用手動API: {setting_id}")
            return True
        else:
            logging.error(f"調用手動API失敗: {setting_id}")
            return False
    else:
        logging.error("沒有拿到setting_ID")
        return False