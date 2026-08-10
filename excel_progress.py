"""從 Google Drive 試算表讀取各 TCG 分頁的「進度」欄位。"""

from __future__ import annotations

import io
import math
import os
import re
from pathlib import Path

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

APP_DIR = Path(__file__).resolve().parent
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
DEFAULT_FILE_ID = "1furK670_lIyKe3kpMRXiaHCt3ajRzJ_-"
DEFAULT_CREDENTIALS = APP_DIR / "tcg-sheet-integration-14bdf407092b.json"

_drive_service = None


def _credentials_path() -> Path:
    env_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return DEFAULT_CREDENTIALS


def parse_google_sheet_id(value: str | None) -> str:
    """從純 ID 或 Google Sheets 網址解析試算表 file ID。"""
    text = (value or "").strip()
    if not text:
        return ""

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", text)
    if match:
        return match.group(1)

    if re.fullmatch(r"[a-zA-Z0-9-_]+", text):
        return text

    raise ValueError(f"無法解析 Google Sheet ID：{text[:120]}")


def _resolve_file_id(google_sheet_id: str | None) -> str:
    parsed = parse_google_sheet_id(google_sheet_id)
    if parsed:
        return parsed
    env_id = os.environ.get("GOOGLE_SHEETS_FILE_ID", "").strip()
    if env_id:
        return env_id
    return DEFAULT_FILE_ID


def _get_drive_service():
    global _drive_service
    if _drive_service is not None:
        return _drive_service

    cred_path = _credentials_path()
    if not cred_path.is_file():
        raise FileNotFoundError(
            f"找不到 Google 服務帳號金鑰：{cred_path}（可設 GOOGLE_SHEETS_CREDENTIALS）"
        )

    creds = service_account.Credentials.from_service_account_file(
        str(cred_path),
        scopes=SCOPES,
    )
    _drive_service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _drive_service


def download_xlsx(google_sheet_id: str | None = None) -> io.BytesIO:
    file_id = _resolve_file_id(google_sheet_id)
    drive_service = _get_drive_service()
    request = drive_service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    file_data.seek(0)
    return file_data


def _json_safe(value):
    """將 pandas / numpy 值轉成 JSON 可序列化格式（NaN → null）。"""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (ValueError, AttributeError):
            pass
    if isinstance(value, (int, str, bool)):
        return value
    if isinstance(value, float):
        return value
    text = str(value).strip()
    return text if text else None


def _parse_progress_rate(df: pd.DataFrame):
    for _, row in df.iterrows():
        for col_idx, cell in enumerate(row):
            if str(cell).strip() == "進度":
                for next_col in range(col_idx + 1, len(row)):
                    if pd.notna(row[next_col]) and str(row[next_col]).strip():
                        return row[next_col]
                break
    return None


def check_progress(google_sheet_id: str | None = None) -> pd.DataFrame:
    """讀取所有 TCG-* 分頁的進度，回傳 DataFrame（分頁名稱、進度）。"""
    file_data = download_xlsx(google_sheet_id)
    xls = pd.ExcelFile(file_data, engine="openpyxl")

    results = []
    for sheet_name in xls.sheet_names:
        if not sheet_name.startswith("TCG-"):
            continue
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        rate = _parse_progress_rate(df)
        results.append({"分頁名稱": sheet_name, "進度": rate})

    return pd.DataFrame(results)


def check_progress_rows(google_sheet_id: str | None) -> list[dict]:
    """回傳 JSON-safe 的進度列表。"""
    file_id = parse_google_sheet_id(google_sheet_id)
    if not file_id:
        raise ValueError("請輸入 Google Sheet ID 或試算表連結")

    df = check_progress(file_id)
    rows = []
    for _, row in df.iterrows():
        rows.append(
            {
                "分頁名稱": str(row["分頁名稱"]),
                "進度": _json_safe(row["進度"]),
            }
        )
    return rows
