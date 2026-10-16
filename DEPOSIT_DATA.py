import logging
from decimal import Decimal

import oracledb

SQL = """
    SELECT DEPOSIT, DEPOSIT_COUNTS
    FROM TCG_ODSDB.ODS_MEMBER_PROFILE
    WHERE CUSTOMER_NAME = :username
      AND MERCHANT_CODE = :merchant_code
"""


def _json_value(value):
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    return value


def get_odsdb_data(username, merchant_code):
    username = (username or "").strip()
    merchant_code = (merchant_code or "").strip()
    if not username or not merchant_code:
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
