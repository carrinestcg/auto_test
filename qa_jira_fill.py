"""把 screenshots/ 的截圖上傳到 Google Drive，並在 Jira 單回填測試結果。"""

from __future__ import annotations

import json
import os
import re
import shutil
import threading
from datetime import datetime
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from excel_progress import _load_service_account_credentials
from jira_drive_comment import JIRA_BASE_URL, JIRA_KEY_RE, JIRA_SSL, parse_ticket_key

APP_DIR = Path(__file__).resolve().parent
SHOT_DIR = APP_DIR / "screenshots"
DONE_DIR = SHOT_DIR / "done"
HISTORY_PATH = APP_DIR / "qa_jira_fill_history.json"
HISTORY_LIMIT = 30

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
_lock = threading.Lock()

load_dotenv(APP_DIR / ".env")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _display_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _safe_name(name: str) -> str:
    base = Path(name or "screenshot").name
    cleaned = re.sub(r"[^\w.\-一-鿿]+", "_", base).strip("._")
    return cleaned or "screenshot"


def list_screenshots():
    """只看 screenshots/ 第一層，已歸檔到 done/ 的不再上傳。"""
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(SHOT_DIR.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_EXTS:
            continue
        files.append({"name": path.name, "size": path.stat().st_size})
    return files


def save_uploads(uploads):
    """表單附上的圖也先放進 screenshots/，跟手動存檔走同一條上傳。"""
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for filename, content, _mime in uploads or []:
        dest = SHOT_DIR / _safe_name(filename)
        if dest.exists():
            dest = SHOT_DIR / f"{dest.stem}_{_now_stamp()}{dest.suffix}"
        dest.write_bytes(content)
        saved.append(dest.name)
    return saved


def _drive_service():
    creds = _load_service_account_credentials(DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


TP_YEAR_RE = re.compile(r"^TP[\s\-]*(20\d{2})$", re.IGNORECASE)
RELEASE_YEAR_RE = re.compile(r"^Release[\s\-]*(20\d{2})$", re.IGNORECASE)


def _parent_folder_id():
    parent = os.environ.get("GOOGLE_DRIVE_PARENT_ID", "").strip()
    if not parent:
        raise FileNotFoundError(
            "未設定 GOOGLE_DRIVE_PARENT_ID。請填 Test Result 的資料夾 ID，只設一次。"
            "裡面要有 Release 2026 與 TP 2026，並分享給服務帳號（編輯者）。"
        )
    return parent


def _is_tp(issue_key="", folder_name=""):
    key = str(issue_key or "").strip().upper()
    if key.startswith("TP"):
        return True
    return bool(re.match(r"^TP[\s\-]*\d", str(folder_name or "").strip(), re.IGNORECASE))


def _list_child_folders(service, parent_id):
    folders = []
    page_token = None
    while True:
        resp = service.files().list(
            q=(
                "mimeType = 'application/vnd.google-apps.folder' "
                f"and '{parent_id}' in parents and trashed = false"
            ),
            fields="nextPageToken, files(id, name, webViewLink)",
            pageSize=100,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            orderBy="name",
        ).execute()
        folders.extend(resp.get("files") or [])
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return [
        {
            "id": item["id"],
            "name": item.get("name") or "",
            "url": item.get("webViewLink") or "",
        }
        for item in folders
    ]


def _year_folder(service, is_tp):
    """TCG 進 Release 2026，TP 進 TP 2026。有指定 ID 就用指定的，否則在 Test Result 底下找今年的資料夾。"""
    env_key = "GOOGLE_DRIVE_TP_FOLDER_ID" if is_tp else "GOOGLE_DRIVE_RELEASE_FOLDER_ID"
    explicit = os.environ.get(env_key, "").strip()
    label = "TP" if is_tp else "Release"
    if explicit:
        return explicit, label
    pattern = TP_YEAR_RE if is_tp else RELEASE_YEAR_RE
    found = []
    for item in _list_child_folders(service, _parent_folder_id()):
        match = pattern.match(item["name"].strip())
        if match:
            found.append((int(match.group(1)), item))
    if not found:
        raise FileNotFoundError(
            f"在 Test Result 底下找不到 {label} 年度資料夾（例如 {label} {datetime.now().year}）。"
        )
    for year, item in found:
        if year == datetime.now().year:
            return item["id"], item["name"]
    found.sort(key=lambda row: row[0], reverse=True)
    return found[0][1]["id"], found[0][1]["name"]


def list_project_folders(query="", issue_key=""):
    """在對應的年度資料夾裡找專案資料夾。"""
    service = _drive_service()
    is_tp = _is_tp(issue_key, query)
    year_id, year_name = _year_folder(service, is_tp)
    folders = _list_child_folders(service, year_id)
    needle = str(query or "").strip().lower()
    if needle:
        folders = [item for item in folders if needle in item["name"].lower()]
    for item in folders:
        item["year"] = year_name
    return folders


def _resolve_project_folder(service, folder_id, folder_name, issue_key):
    folder_id = str(folder_id or "").strip()
    folder_name = str(folder_name or "").strip()
    is_tp = _is_tp(issue_key, folder_name)
    year_id, year_name = _year_folder(service, is_tp)
    if folder_id:
        return folder_id, folder_name or folder_id, year_name
    if not folder_name:
        raise ValueError("請填專案資料夾，例如 TP-5299")

    matches = list_project_folders(folder_name, issue_key)
    exact = [item for item in matches if item["name"].lower() == folder_name.lower()]
    if len(exact) == 1:
        return exact[0]["id"], exact[0]["name"], year_name
    if len(matches) > 1:
        names = "、".join(item["name"] for item in matches[:8])
        raise ValueError(f"找到多個專案資料夾，請選一個：{names}")
    if len(matches) == 1:
        return matches[0]["id"], matches[0]["name"], year_name

    created = service.files().create(
        body={
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [year_id],
        },
        fields="id, name",
        supportsAllDrives=True,
    ).execute()
    return created["id"], created.get("name") or folder_name, year_name


def _share_reader(service, file_id):
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
        supportsAllDrives=True,
    ).execute()


def _upload_folder(service, issue_key, paths, project_folder_id):
    parent = project_folder_id
    folder_name = f"{issue_key}_{_now_stamp()}"
    folder = service.files().create(
        body={
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent],
        },
        fields="id, webViewLink",
        supportsAllDrives=True,
    ).execute()
    folder_id = folder["id"]
    share_note = ""
    try:
        _share_reader(service, folder_id)
    except Exception as exc:
        share_note = f"資料夾已建立，但無法設成任何人可看連結：{exc}"

    uploaded = []
    for path in paths:
        media = MediaFileUpload(str(path), resumable=False)
        created = service.files().create(
            body={"name": path.name, "parents": [folder_id]},
            media_body=media,
            fields="id, name, webViewLink",
            supportsAllDrives=True,
        ).execute()
        try:
            _share_reader(service, created["id"])
        except Exception:
            if not share_note:
                share_note = "檔案已上傳，但無法設成任何人可看連結，請確認資料夾分享權限。"
        uploaded.append({
            "name": created.get("name") or path.name,
            "url": created.get("webViewLink") or f"https://drive.google.com/file/d/{created['id']}/view",
        })

    folder_url = folder.get("webViewLink") or f"https://drive.google.com/drive/folders/{folder_id}"
    return folder_name, folder_url, uploaded, share_note


def _comment_body(result, note, folder_url, files):
    headline = "QA verified Pass:" if result == "PASS" else "QA verified Fail:"
    lines = [
        headline,
        f"Test result link: {folder_url}",
    ]
    if note:
        lines.extend(["", note])
    if files:
        lines.extend(["", "圖片："])
        lines.extend(f"- {item['name']} {item['url']}" for item in files)
    return "\n".join(lines)


def _jira_headers():
    token = os.getenv("JIRA_TOKEN")
    if not token:
        raise FileNotFoundError("未設定 JIRA_TOKEN")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _add_comment(issue_key, body):
    resp = requests.post(
        f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/comment",
        headers=_jira_headers(),
        json={"body": body},
        verify=JIRA_SSL,
        timeout=30,
    )
    if not resp.ok:
        detail = resp.text[:300] or resp.reason
        raise requests.HTTPError(f"Jira 回填失敗（{resp.status_code}）：{detail}", response=resp)
    data = resp.json()
    comment_id = str(data.get("id") or "")
    comment_url = f"{JIRA_BASE_URL}/browse/{issue_key}?focusedCommentId={comment_id}" if comment_id else f"{JIRA_BASE_URL}/browse/{issue_key}"
    return comment_id, comment_url


def _archive(paths, issue_key):
    dest_dir = DONE_DIR / f"{issue_key}_{_now_stamp()}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if path.is_file():
            shutil.move(str(path), dest_dir / path.name)
    return str(dest_dir.relative_to(APP_DIR))


def _read_history():
    if not HISTORY_PATH.is_file():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _append_history(record):
    with _lock:
        rows = _read_history()
        rows.insert(0, record)
        HISTORY_PATH.write_text(
            json.dumps(rows[:HISTORY_LIMIT], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_history(limit=10):
    return _read_history()[:limit]


def _shot_paths():
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    return [
        path for path in sorted(SHOT_DIR.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() in IMAGE_EXTS
    ]


def fill(issue_raw, result, note="", uploads=None, folder_id="", folder_name=""):
    issue_key = parse_ticket_key(issue_raw)
    if not issue_key or not JIRA_KEY_RE.fullmatch(issue_key):
        raise ValueError("請填 Jira 單號，例如 TCG-12345")
    result = str(result or "").strip().upper()
    if result not in {"PASS", "FAIL"}:
        raise ValueError("測試結果請選 PASS 或 FAIL")
    note = str(note or "").strip()

    save_uploads(uploads)
    paths = _shot_paths()
    if not paths:
        raise ValueError("screenshots 資料夾沒有截圖。請先把圖存進去，或在表單選擇圖片。")

    record = {
        "time": _display_time(),
        "jira": issue_key,
        "result": result,
        "note": note,
        "success": False,
        "year_folder": "",
        "project_folder": "",
        "folder_url": "",
        "files": [],
        "comment_url": "",
        "message": "",
    }
    try:
        service = _drive_service()
        project_id, project_name, year_name = _resolve_project_folder(
            service, folder_id, folder_name, issue_key
        )
        record["year_folder"] = year_name
        record["project_folder"] = project_name
        _folder_name, folder_url, files, share_note = _upload_folder(service, issue_key, paths, project_id)
        record["folder_url"] = folder_url
        record["files"] = files
        comment_id, comment_url = _add_comment(
            issue_key, _comment_body(result, note, folder_url, files)
        )
        record["comment_url"] = comment_url
        record["comment_id"] = comment_id
        archived = _archive(paths, issue_key)
        record["archived"] = archived
        record["success"] = True
        message = f"{issue_key} 已回填{result}（{year_name} / {project_name}）"
        if share_note:
            message = f"{message}。{share_note}"
        record["message"] = message
    except Exception as exc:
        record["message"] = str(exc)
        _append_history(record)
        return record
    _append_history(record)
    return record
