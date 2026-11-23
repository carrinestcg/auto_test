import requests
import logging
import urllib3
from DB_connect import DB_execute
from datetime import datetime, timedelta
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def update_promotion_setting_time (promotion_id):
    today = datetime.now().strftime("%Y-%m-%d")
    SQL = f"""
    UPDATE TCG_MCSDB.MCS_PROMOTION_SETTING
    SET START_TIME = TO_TIMESTAMP('{today} 00:00:00.000', 'YYYY-MM-DD HH24:MI:SS.FF3')
    WHERE ID = '{promotion_id}'
    """
    return DB_execute(SQL)

def update_promotion_audit_time (promotion_id):
    today = datetime.now().strftime("%Y-%m-%d")
    SQL = f"""
    UPDATE TCG_MCSDB.PROMO_QUEST_DISPATCH_AUDIT_SUMMARY
    SET LAST_PROCESS_TIME = TO_TIMESTAMP('{today} 00:00:00.000', 'YYYY-MM-DD HH24:MI:SS.FF3')
    WHERE PROMOTION_ID = '{promotion_id}'
    """
    return DB_execute(SQL)
    
def main(PROMOTION_ID):
    
    if PROMOTION_ID:
        logging.info(f"拿到setting_ID: {PROMOTION_ID}")
        update_promotion_setting_time(PROMOTION_ID)
        update_promotion_audit_time(PROMOTION_ID)
        return True
        
    else:
        logging.error("沒有拿到PROMOTION_ID")
        return False