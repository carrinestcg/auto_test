import logging
from decimal import Decimal

import oracledb

SQL = """
    SELECT DEPOSIT, DEPOSIT_COUNTS
    FROM TCG_ODSDB.ODS_MEMBER_PROFILE
    WHERE CUSTOMER_NAME = :username
      AND MERCHANT_CODE = :merchant_code
"""
SQL_FOR_COUNT = """
    SELECT CUSTOMER_NAME
    FROM TCG_ODSDB.ODS_MEMBER_PROFILE
    WHERE DEPOSIT_COUNTS = :deposit_counts
      AND MERCHANT_CODE = :merchant_code
      AND REG_DATE >= TO_TIMESTAMP('2026-10-08 00:00:00.000', 'YYYY-MM-DD HH24:MI:SS.FF3')
    ORDER BY CUSTOMER_NAME
    FETCH FIRST 30 ROWS ONLY
"""
SQL_FOR_COUNT_TOTAL = """
    SELECT COUNT(*)
    FROM TCG_ODSDB.ODS_MEMBER_PROFILE
    WHERE DEPOSIT_COUNTS = :deposit_counts
      AND MERCHANT_CODE = :merchant_code
      AND REG_DATE >= TO_TIMESTAMP('2026-10-08 00:00:00.000', 'YYYY-MM-DD HH24:MI:SS.FF3')
"""

SQL_FOR_BET="""
       SELECT tms.PVP_VALID_GAME_BETTING,
       tms.RNG_VALID_GAME_BETTING,
       tms.LIVE_VALID_GAME_BETTING,
       tms.ELOTT_VALID_GAME_BETTING,
       tms.LOTT_VALID_GAME_BETTING,
       tms.FISH_VALID_GAME_BETTING,
       tms.SPORTS_VALID_GAME_BETTING,
       NVL(tms.PVP_VALID_GAME_BETTING, 0)
     + NVL(tms.RNG_VALID_GAME_BETTING, 0)
     + NVL(tms.LIVE_VALID_GAME_BETTING, 0)
     + NVL(tms.ELOTT_VALID_GAME_BETTING, 0)
     + NVL(tms.LOTT_VALID_GAME_BETTING, 0)
     + NVL(tms.FISH_VALID_GAME_BETTING, 0)
     + NVL(tms.SPORTS_VALID_GAME_BETTING, 0) AS TOTAL_VALID_BETTING
FROM TCG_ODSDB.ODS_MEMBER_PROFILE tms
WHERE tms.CUSTOMER_ID = :customer_id
"""
def _json_value(value):
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    return value


def _odsdb_connect():
    return oracledb.connect(
        user="TCG_ODSDB",
        password="3JAqs3RpSnsw99SF",
        dsn="10.81.1.11:1521/tcgsit",
    )


def get_customers_by_deposit_count(merchant_code, deposit_counts):
    """只找出 DEPOSIT_COUNTS 等於指定次數的玩家。"""
    merchant_code = (merchant_code or "").strip()
    if not merchant_code or deposit_counts is None:
        return None

    conn = None
    cursor = None
    try:
        conn = _odsdb_connect()
        cursor = conn.cursor()
        params = {"deposit_counts": deposit_counts, "merchant_code": merchant_code}
        cursor.execute(SQL_FOR_COUNT_TOTAL, params)
        total_row = cursor.fetchone()
        total = int(total_row[0]) if total_row and total_row[0] is not None else 0
        if total == 0:
            logging.info("查無存款次數 deposit_counts=%s merchant=%s", deposit_counts, merchant_code)
            return None
        cursor.execute(SQL_FOR_COUNT, params)
        columns = [desc[0] for desc in cursor.description]
        customers = []
        for row in cursor.fetchall():
            record = {col: _json_value(val) for col, val in zip(columns, row)}
            customers.append({
                "customer_name": record.get("CUSTOMER_NAME"),
            })
        return {
            "deposit_counts": deposit_counts,
            "total": total,
            "customers": customers,
        }
    except Exception as e:
        logging.error("依存款次數查玩家失敗: %s", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_odsdb_data(username, merchant_code, deposit_counts=None):
    username = (username or "").strip()
    merchant_code = (merchant_code or "").strip()
    if deposit_counts is not None:
        return get_customers_by_deposit_count(merchant_code, deposit_counts)
    if not username or not merchant_code:
        return None

    conn = None
    cursor = None
    try:
        conn = _odsdb_connect()
        cursor = conn.cursor()
        cursor.execute(SQL, {"username": username, "merchant_code": merchant_code})
        row = cursor.fetchone()
        if not row:
            logging.info("查無存款統計 username=%s merchant=%s", username, merchant_code)
            return None
        columns = [desc[0] for desc in cursor.description]
        record = {col: _json_value(val) for col, val in zip(columns, row)}
        return {
            "deposit": record.get("DEPOSIT"),
            "deposit_counts": record.get("DEPOSIT_COUNTS"),
        }
    except Exception as e:
        logging.error("存款統計查詢失敗: %s", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_odsdb_data_bet(customer_id):
    customer_id = str(customer_id or "").strip()
    if not customer_id:
        return None

    conn = None
    cursor = None
    try:
        conn = oracledb.connect(
            user="TCG_ODSDB",
            password="3JAqs3RpSnsw99SF",
            dsn="10.81.1.11:1521/tcgsit",
        )
        cursor = conn.cursor()
        cursor.execute(SQL_FOR_BET, {"customer_id": customer_id})
        row = cursor.fetchone()
        if not row:
            logging.info("查無投注統計 customer_id=%s", customer_id)
            return None
        columns = [desc[0] for desc in cursor.description]
        record = {col: _json_value(val) for col, val in zip(columns, row)}
        return {
            "bet_amount": record.get("TOTAL_VALID_BETTING"),
            "RNG": record.get("RNG_VALID_GAME_BETTING"),
            "PVP": record.get("PVP_VALID_GAME_BETTING"),
            "LIVE": record.get("LIVE_VALID_GAME_BETTING"),  
            "ELOTT": record.get("ELOTT_VALID_GAME_BETTING"),
            "LOTT": record.get("LOTT_VALID_GAME_BETTING"),
            "FISH": record.get("FISH_VALID_GAME_BETTING"),
            "SPORTS": record.get("SPORTS_VALID_GAME_BETTING")
        }
    except Exception as e:
        logging.error("投注統計查詢失敗: %s", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
