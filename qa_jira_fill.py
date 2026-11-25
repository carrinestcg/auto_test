"""把 screenshots/ 的截圖上傳到 Google Drive，並在 Jira 單回填測試結果。"""

from __future__ import annotations

import json
import os
import re
import shutil
import threading
import time
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


def save_uploads(uploads, dest_dir=None):
    """表單附上的圖寫進 dest_dir（預設 screenshots/）。回傳 Path 清單。"""
    dest_dir = Path(dest_dir) if dest_dir else SHOT_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for filename, content, _mime in uploads or []:
        dest = dest_dir / _safe_name(filename)
        if dest.exists():
            dest = dest_dir / f"{dest.stem}_{_now_stamp()}{dest.suffix}"
        dest.write_bytes(content)
        saved.append(dest)
    return saved


OAUTH_TOKEN_PATH = APP_DIR / "drive_oauth_token.json"


def _oauth_client_path():
    env_path = os.environ.get("GOOGLE_OAUTH_CLIENT_JSON", "").strip()
    if not env_path:
        return None
    path = Path(env_path).expanduser()
    if not path.is_absolute():
        path = (APP_DIR / path).resolve()
    return path


def _user_credentials():
    """擁有者授權一次後留下的 token。沒有這個檔就改走服務帳號。"""
    if not OAUTH_TOKEN_PATH.is_file():
        return None
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(str(OAUTH_TOKEN_PATH), DRIVE_SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        OAUTH_TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    if not creds.valid:
        raise RuntimeError("Drive 授權已失效，請在這台有瀏覽器的機器重跑 authorize_drive.py")
    return creds


def _drive_service():
    creds = _user_credentials() or _load_service_account_credentials(DRIVE_SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def authorize_drive():
    """開瀏覽器讓資料夾擁有者登入一次，並把 refresh token 存到本機。"""
    client_path = _oauth_client_path()
    if client_path is None or not client_path.is_file():
        raise FileNotFoundError(
            "找不到 OAuth 用戶端 JSON。請在 .env 設定 GOOGLE_OAUTH_CLIENT_JSON"
        )
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(client_path), DRIVE_SCOPES)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    OAUTH_TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return OAUTH_TOKEN_PATH


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


def _resolve_project_folder(service, folder_id, folder_name, issue_key, create=True):
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

    if not create:
        raise ValueError(f"找不到專案資料夾「{folder_name}」。請先在 Drive 建好，或從清單選一個。")

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


def list_ticket_folders(parent_id="", parent_name="", query=""):
    """列出 TP 專案底下的 TCG 單資料夾。"""
    service = _drive_service()
    parent_id = str(parent_id or "").strip()
    if not parent_id:
        parent_id, _name, _year = _resolve_project_folder(service, "", parent_name, "TP-1")
    folders = _list_child_folders(service, parent_id)
    needle = str(query or "").strip().lower()
    if needle:
        folders = [item for item in folders if needle in item["name"].lower()]
    return folders


def _resolve_ticket_folder(service, project_id, project_name, issue_key, ticket_id, ticket_name, create=True):
    """TP 專案底下再找 TCG 單資料夾。Release 的專案資料夾本身就是單號，不再往下拆。"""
    if not re.match(r"^TP[\s\-]*\d", str(project_name or ""), re.IGNORECASE):
        return project_id, ""
    if not str(issue_key or "").upper().startswith("TCG"):
        return project_id, ""

    children = _list_child_folders(service, project_id)
    ticket_id = str(ticket_id or "").strip()
    ticket_name = str(ticket_name or "").strip()
    if ticket_id:
        chosen = next((item for item in children if item["id"] == ticket_id), None)
        if chosen:
            return chosen["id"], chosen["name"]
        return ticket_id, ticket_name or ticket_id

    key = issue_key.upper()
    prefixed = [item for item in children if item["name"].upper().startswith(key)]
    if ticket_name:
        named = [item for item in children if ticket_name.lower() in item["name"].lower()]
        if len(named) == 1:
            return named[0]["id"], named[0]["name"]
        if len(named) > 1:
            names = "、".join(item["name"] for item in named[:8])
            raise ValueError(f"找到多個 TCG 資料夾，請選一個：{names}")
    if len(prefixed) == 1:
        return prefixed[0]["id"], prefixed[0]["name"]
    if len(prefixed) > 1:
        names = "、".join(item["name"] for item in prefixed[:8])
        raise ValueError(f"找到多個 TCG 資料夾，請選一個：{names}")

    if not create:
        raise ValueError(f"找不到 {issue_key} 的資料夾。請先在 Drive 放好檔案，再從清單選這個資料夾。")

    created = service.files().create(
        body={
            "name": issue_key,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [project_id],
        },
        fields="id, name",
        supportsAllDrives=True,
    ).execute()
    return created["id"], created.get("name") or issue_key


def _folder_link(service, folder_id):
    meta = service.files().get(
        fileId=folder_id,
        fields="id, webViewLink",
        supportsAllDrives=True,
    ).execute()
    return meta.get("webViewLink") or f"https://drive.google.com/drive/folders/{folder_id}"


def _share_reader(service, file_id):
    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
        fields="id",
        supportsAllDrives=True,
    ).execute()


def _call_with_retry(fn, attempts=3, delay=1.2):
    last = None
    for index in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last = exc
            if index < attempts - 1:
                time.sleep(delay * (index + 1))
    raise last


def _upload_one_file(service, path, folder_id):
    media = MediaFileUpload(str(path), resumable=False)
    created = service.files().create(
        body={"name": path.name, "parents": [folder_id]},
        media_body=media,
        fields="id, name, webViewLink",
        supportsAllDrives=True,
    ).execute()
    try:
        _share_reader(service, created["id"])
        share_ok = True
    except Exception:
        share_ok = False
    return {
        "name": created.get("name") or path.name,
        "url": created.get("webViewLink") or f"https://drive.google.com/file/d/{created['id']}/view",
        "share_ok": share_ok,
    }


def _upload_folder(service, issue_key, paths, project_folder_id):
    parent = project_folder_id
    folder_name = f"{issue_key}_{_now_stamp()}"

    def create_folder():
        return service.files().create(
            body={
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent],
            },
            fields="id, webViewLink",
            supportsAllDrives=True,
        ).execute()

    folder = _call_with_retry(create_folder)
    folder_id = folder["id"]
    share_note = ""
    try:
        _share_reader(service, folder_id)
    except Exception as exc:
        share_note = f"資料夾已建立，但無法設成任何人可看連結：{exc}"

    uploaded = []
    for path in paths:
        item = _call_with_retry(lambda p=path: _upload_one_file(service, p, folder_id))
        if not item.pop("share_ok", True) and not share_note:
            share_note = "檔案已上傳，但無法設成任何人可看連結，請確認資料夾分享權限。"
        uploaded.append(item)

    folder_url = folder.get("webViewLink") or f"https://drive.google.com/drive/folders/{folder_id}"
    return folder_name, folder_url, uploaded, share_note


def _comment_body(result, note, folder_url, files, path_label=""):
    headline = "QA verified Pass:" if result == "PASS" else "QA verified Fail:"
    lines = [
        headline,
        f"Test result link: {folder_url}",
    ]
    if path_label:
        lines.append(f"Drive 路徑：{path_label}")
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


_QA_DONE_STATUSES = {"closed", "resolved", "done", "cancelled", "canceled"}


def _jira_get(path, params=None):
    resp = requests.get(
        f"{JIRA_BASE_URL}{path}",
        headers=_jira_headers(),
        params=params,
        verify=JIRA_SSL,
        timeout=30,
    )
    if not resp.ok:
        detail = resp.text[:300] or resp.reason
        raise requests.HTTPError(f"Jira 讀取失敗（{resp.status_code}）：{detail}", response=resp)
    return resp.json()


def _issue_type_name(fields):
    itype = (fields or {}).get("issuetype") or {}
    return str(itype.get("name") or "").strip()


def _status_name(fields):
    status = (fields or {}).get("status") or {}
    return str(status.get("name") or "").strip()


def _is_qa_task(fields):
    return _issue_type_name(fields).lower() == "qa task"


def _status_done(name):
    return str(name or "").strip().lower() in _QA_DONE_STATUSES


def _parse_task_type(value):
    try:
        kind = int(value)
    except (TypeError, ValueError):
        kind = 1
    return 2 if kind == 2 else 1


def _is_sanity_summary(summary):
    return "sanity" in str(summary or "").lower()


def _matches_task_type(summary, task_type):
    sanity = _is_sanity_summary(summary)
    return sanity if task_type == 2 else not sanity


def _qa_task_score(summary, status, task_type=1):
    score = 0
    title = str(summary or "")
    st = str(status or "").strip().lower()
    if _status_done(st):
        score -= 50
    elif st == "in progress":
        score += 100
    elif st == "open":
        score += 40
    else:
        score += 20
    if title.startswith("[QA][PED]"):
        score += 20
    if task_type == 2 and _is_sanity_summary(title):
        score += 10
    elif task_type != 2 and "測試" in title:
        score += 10
    return score


def _resolve_qa_task(issue_key, task_type=1):
    """留言與結案目標是 QA Task。填主單時依類型找一般測試或 Sanity Test；Drive 仍用主單號。"""
    task_type = _parse_task_type(task_type)
    type_label = "Sanity Test" if task_type == 2 else "一般 QA Task"
    data = _jira_get(
        f"/rest/api/2/issue/{issue_key}",
        params={"fields": "summary,issuetype,status,subtasks,parent"},
    )
    fields = data.get("fields") or {}
    if _is_qa_task(fields):
        parent = ((fields.get("parent") or {}).get("key") or "").strip()
        return {
            "qa_key": issue_key,
            "drive_key": parent or issue_key,
            "parent_key": parent,
            "qa_summary": fields.get("summary") or "",
            "qa_status": _status_name(fields),
            "task_type": task_type,
        }

    candidates = []
    for item in fields.get("subtasks") or []:
        sub_fields = item.get("fields") or {}
        if not _is_qa_task(sub_fields) and _issue_type_name(sub_fields):
            continue
        summary = str(sub_fields.get("summary") or "")
        if not _is_qa_task(sub_fields):
            if not summary.startswith("[QA][PED]") and "QA Task" not in summary:
                continue
        if not _matches_task_type(summary, task_type):
            continue
        key = str(item.get("key") or "").strip()
        if not key:
            continue
        status = _status_name(sub_fields)
        candidates.append((_qa_task_score(summary, status, task_type), key, summary, status))

    if not candidates:
        raise ValueError(
            f"{issue_key} 底下找不到 {type_label}。"
            "請先建立對應的 QA Task，或把 Jira 單號改成那張 QA Task。"
        )
    candidates.sort(key=lambda row: row[0], reverse=True)
    _score, qa_key, summary, status = candidates[0]
    return {
        "qa_key": qa_key,
        "drive_key": issue_key,
        "parent_key": issue_key,
        "qa_summary": summary,
        "qa_status": status,
        "task_type": task_type,
    }


def _pick_resolve_transition(transitions):
    rows = []
    for item in transitions or []:
        name = str(item.get("name") or "").strip()
        to_name = str(((item.get("to") or {}).get("name")) or "").strip()
        tid = str(item.get("id") or "").strip()
        if not tid:
            continue
        lowered = name.lower()
        to_lower = to_name.lower()
        score = 0
        if to_lower == "resolved":
            score += 80
        elif to_lower in {"closed", "done"}:
            score += 60
        if "resolv" in lowered:
            score += 40
        if "verified" in lowered:
            score += 50
        if "close" in lowered or lowered == "done":
            score += 20
        if score:
            rows.append((score, tid, name, to_name))
    if not rows:
        return None
    rows.sort(key=lambda row: row[0], reverse=True)
    return rows[0]


def _transition_qa_resolved(qa_key):
    """In Progress 的 QA Task 工作流沒有 Resolved，對應動作是 Verified → Closed。"""
    issue = _jira_get(
        f"/rest/api/2/issue/{qa_key}",
        params={"fields": "status"},
    )
    current = _status_name(issue.get("fields") or {})
    if _status_done(current):
        return f"狀態已是 {current}，略過轉換"

    data = _jira_get(f"/rest/api/2/issue/{qa_key}/transitions")
    picked = _pick_resolve_transition(data.get("transitions") or [])
    if not picked:
        names = [str(item.get("name") or "") for item in (data.get("transitions") or [])]
        raise ValueError(
            f"{qa_key} 目前是 {current or '未知狀態'}，沒有可用的 resolve / Verified 轉換"
            + (f"（現有：{'、'.join(names)}）" if names else "")
        )
    _score, tid, name, to_name = picked
    resp = requests.post(
        f"{JIRA_BASE_URL}/rest/api/2/issue/{qa_key}/transitions",
        headers=_jira_headers(),
        json={"transition": {"id": tid}},
        verify=JIRA_SSL,
        timeout=30,
    )
    if not resp.ok:
        detail = resp.text[:300] or resp.reason
        raise requests.HTTPError(
            f"{qa_key} 狀態轉換失敗（{resp.status_code}）：{detail}",
            response=resp,
        )
    return f"{current} → {to_name}（{name}）"


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
    parents = set()
    for path in paths:
        if path.is_file():
            parents.add(path.parent)
            shutil.move(str(path), dest_dir / path.name)
    for folder in parents:
        if folder != SHOT_DIR and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    return str(dest_dir.relative_to(APP_DIR))


def _discard_staging(paths):
    """失敗後只清掉這次暫存檔，不留本機殘檔給下一張票。"""
    parents = set()
    for path in paths or []:
        if path.parent != SHOT_DIR and path.is_file():
            parents.add(path.parent)
            path.unlink(missing_ok=True)
    for folder in parents:
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()


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


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def fill(issue_raw, result, note="", uploads=None, folder_id="", folder_name="", ticket_folder_id="", ticket_folder_name="", link_only=False, task_type=1):
    issue_key = parse_ticket_key(issue_raw)
    if not issue_key or not JIRA_KEY_RE.fullmatch(issue_key):
        raise ValueError("請填 Jira 單號，例如 TCG-12345")
    result = str(result or "").strip().upper()
    if result not in {"PASS", "FAIL"}:
        raise ValueError("測試結果請選 PASS 或 FAIL")
    note = str(note or "").strip()
    task_type = _parse_task_type(task_type)
    target = _resolve_qa_task(issue_key, task_type)
    qa_key = target["qa_key"]
    drive_key = target["drive_key"]

    link_only = _as_bool(link_only)
    uploads = uploads or []
    if link_only:
        paths = []
    elif uploads:
        # 這次表單選的圖單獨一夾，不跟 screenshots/ 上一批殘檔混在一起
        staging = SHOT_DIR / f"_run_{drive_key}_{_now_stamp()}"
        paths = save_uploads(uploads, staging)
    else:
        paths = _shot_paths()

    record = {
        "time": _display_time(),
        "jira": drive_key,
        "qa_task": qa_key,
        "task_type": task_type,
        "result": result,
        "note": note,
        "success": False,
        "year_folder": "",
        "project_folder": "",
        "ticket_folder": "",
        "folder_url": "",
        "files": [],
        "comment_url": "",
        "status_change": "",
        "message": "",
    }
    try:
        service = _drive_service()
        project_id, project_name, year_name = _resolve_project_folder(
            service, folder_id, folder_name, drive_key, create=bool(paths)
        )
        record["year_folder"] = year_name
        record["project_folder"] = project_name
        ticket_id, ticket_name = _resolve_ticket_folder(
            service, project_id, project_name, drive_key, ticket_folder_id, ticket_folder_name, create=bool(paths)
        )
        record["ticket_folder"] = ticket_name
        upload_folder_name = ""
        if paths:
            upload_folder_name, folder_url, files, share_note = _upload_folder(service, drive_key, paths, ticket_id)
        else:
            folder_url = _folder_link(service, ticket_id)
            files = []
            share_note = "已貼上既有資料夾連結，沒有上傳圖片。"
        record["folder_url"] = folder_url
        record["files"] = files
        path_label = " / ".join(
            part for part in (year_name, project_name, ticket_name, upload_folder_name) if part
        )
        comment_id, comment_url = _add_comment(
            qa_key, _comment_body(result, note, folder_url, files, path_label)
        )
        record["comment_url"] = comment_url
        record["comment_id"] = comment_id
        record["drive_path"] = path_label
        status_note = ""
        if result == "PASS":
            try:
                record["status_change"] = _transition_qa_resolved(qa_key)
            except Exception as exc:
                status_note = f"留言已貼上，但狀態沒轉成功：{exc}"
        if paths:
            archived = _archive(paths, drive_key)
            record["archived"] = archived
        record["success"] = True
        message = f"{qa_key} 已回填 {result}（{path_label}）"
        if drive_key != qa_key:
            message = f"{drive_key} 的 QA Task {message}"
        if record.get("status_change"):
            message = f"{message}。狀態 {record['status_change']}"
        if status_note:
            message = f"{message}。{status_note}"
        if share_note:
            message = f"{message}。{share_note}"
        record["message"] = message
    except Exception as exc:
        record["message"] = str(exc)
        _discard_staging(paths)
        _append_history(record)
        return record
    _append_history(record)
    return record
