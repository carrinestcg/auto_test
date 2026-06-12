from datetime import datetime
import oracledb
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

_pool: Optional[oracledb.ConnectionPool] = None

def get_pool() -> oracledb.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(
            user="TCG_MCSDB",
            password="Jv7UrDc7rsqJ87Km",
            dsn="10.81.1.11:1521/tcgsit",
            min=2,
            max=10,
            increment=1,
        )
    return _pool

def DB_connect(SQL: str, params: dict) -> list[dict] | None:

    logging.info("SQL: %s | params: %s", SQL, params)
    pool = get_pool()
    with pool.acquire() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(SQL, params)   # ✅ Bind variables，防 injection + 快取執行計劃
                rows = cursor.fetchall()
                if not rows:
                    logging.info("查無資料")
                    return None

                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in rows:
                    record = {}
                    for col, val in zip(columns, row):
                        if isinstance(val, datetime):
                            record[col] = val.strftime('%Y-%m-%d %H:%M:%S')
                        elif val is None:
                            record[col] = None
                        else:
                            record[col] = val
                    results.append(record)

                _print_results(results)
                return results

            except oracledb.DatabaseError as e:
                logging.error("❌ 資料庫錯誤: %s", e)
                return None
            
def _print_results(results: list[dict]):
    for record in results:
        print("=" * 60)
        print("資訊")
        print("=" * 60)
        for col, val in record.items():
            display = '(空白)' if val == " " else ('NULL' if val is None else str(val))
            print(f"{col:25s}: {display}")
            
def main(username: str, platform, query_type: int) -> str | None:
    if isinstance(platform, (list, tuple)):
        platform = platform[0] if platform else "gi8viet"
    platform = (platform or "gi8viet").strip()
    username = (username or "").strip()

    customer_name = username if "@" in username else f"{platform}@{username}"

    if query_type == 1:
        # ✅ Bind variable 用 :name 佔位符
        rows = DB_connect(
            "SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE UPPER(CUSTOMER_NAME) = UPPER(:name)",
            {"name": customer_name}
        )
        return rows[0]["CUSTOMER_ID"] if rows else None

    elif query_type == 2:
        rows = DB_connect(
            "SELECT CUSTOMER_NAME FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_ID = :id",
            {"id": username}
        )
        return rows[0]["CUSTOMER_NAME"] if rows else None

    return None
