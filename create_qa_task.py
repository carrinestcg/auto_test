import re
import requests
import urllib3
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============ 設定區 ============
JIRA_BASE_URL = "https://jira.tc-gaming.co/jira"
JIRA_TOKEN    = os.getenv("JIRA_TOKEN")
JIRA_SSL      = False

ASSIGNEE      = "carrine.s"
# ================================

HEADERS = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Content-Type": "application/json"
}

PED_ICR_RE = re.compile(r"\[PED\]\s+ICR\s+(\d{4}-\d{2})", re.IGNORECASE)


def current_ped_icr_label(when=None):
    stamp = when or datetime.now()
    return f"[PED] ICR {stamp.strftime('%Y-%m')}"


def _ped_icr_month(name):
    match = PED_ICR_RE.search(str(name or ""))
    return match.group(1) if match else ""


def _pick_ped_icr_version(versions, target_month):
    """用 [PED] ICR YYYY-MM 關鍵字挑版本，不依賴 TP 號碼。"""
    scored = []
    for version in versions or []:
        if version.get("archived"):
            continue
        name = str(version.get("name") or "")
        month = _ped_icr_month(name)
        if not month:
            continue
        scored.append((month, len(name), version))
    if not scored:
        return None

    def shortest(rows):
        rows.sort(key=lambda row: row[1])
        return rows[0][2]

    current = [row for row in scored if row[0] == target_month]
    if current:
        return shortest(current)
    past = [row for row in scored if row[0] <= target_month]
    if not past:
        return None
    latest = max(row[0] for row in past)
    return shortest([row for row in past if row[0] == latest])


def resolve_ped_icr_fix_versions(when=None):
    """QA Task 的 Fix Version 用關鍵字 [PED] ICR YYYY-MM。當月還沒開就用最近一個已存在的月版本。"""
    stamp = when or datetime.now()
    target = stamp.strftime("%Y-%m")
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/project/TCG/versions",
        headers=HEADERS,
        verify=JIRA_SSL,
        timeout=30,
    )
    resp.raise_for_status()
    chosen = _pick_ped_icr_version(resp.json() or [], target)
    if not chosen:
        raise ValueError(
            f"找不到 Fix Version（名稱需含 [PED] ICR YYYY-MM，例如 {current_ped_icr_label(stamp)}）。"
        )
    return [{"name": chosen["name"]}]


def get_issue(issue_key):
    """抓原始 TCG 單的資料"""
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}",
        headers=HEADERS,
        verify=JIRA_SSL
    )
    resp.raise_for_status()
    fields = resp.json()["fields"]
    summary     = fields.get("summary", "")
    reporter    = fields.get("reporter", {}).get("name", ASSIGNEE)
    return summary, reporter

def search_users(query, limit=15):
    """Jira 使用者 typeahead，回傳格式與 Component 相同（name = username）。"""
    needle = (query or "").strip()
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/user/picker",
        headers=HEADERS,
        params={"query": needle, "maxResults": limit},
        verify=JIRA_SSL,
        timeout=20,
    )
    resp.raise_for_status()
    matches = []
    for user in (resp.json() or {}).get("users") or []:
        name = (user.get("name") or user.get("key") or "").strip()
        if not name:
            continue
        matches.append({
            "name": name,
            "summary": user.get("displayName") or name,
        })
        if len(matches) >= limit:
            break
    return matches


def resolve_assignee_name(query, fallback=""):
    raw = (query or "").strip()
    if not raw:
        return (fallback or ASSIGNEE).strip()
    try:
        users = search_users(raw, limit=15)
    except Exception:
        users = []
    lowered = raw.lower()
    for user in users:
        if user["name"].lower() == lowered:
            return user["name"]
    for user in users:
        if (user.get("summary") or "").lower() == lowered:
            return user["name"]
    if len(users) == 1:
        return users[0]["name"]
    return raw


def qa_task_title(summary, tasktype):
    """Tasktype 1 一般測試，2 為 Sanity Test。"""
    try:
        kind = int(tasktype)
    except (TypeError, ValueError):
        kind = 1
    if kind == 2:
        return f"[QA][PED] Sanity Test {summary}"
    return f"[QA][PED] 測試 {summary}"


def create_qa_task(tcg_key, summary, reporter=None, Tasktype=1, assignee=None, fix_versions=None):
    """在 TCG 單底下建立 QA Task subtask，建立後轉為 In Progress"""
    new_summary = qa_task_title(summary, Tasktype)
    assignee_name = resolve_assignee_name(assignee, fallback=ASSIGNEE)
    versions = fix_versions if fix_versions is not None else resolve_ped_icr_fix_versions()

    fields = {
            "project": {"key": "TCG"},
            "parent": {"key": tcg_key},
            "summary": new_summary,
            "issuetype": {"name": "QA Task"},
            "assignee": {"name": assignee_name},
            "fixVersions": versions,
            "customfield_10000": {"value": "TCG"},
            "components": [{"id": "13316"}],
        }
    resp = requests.post(
        f"{JIRA_BASE_URL}/rest/api/2/issue",
        headers=HEADERS,
        json={"fields": fields},
        verify=JIRA_SSL
    )

    if resp.status_code not in (200, 201):
        print(f"❌ 建立失敗：{resp.status_code} {resp.text}")
        return None

    new_key = resp.json().get("key")

    # 查可用 transitions 並轉為 In Progress
    t_resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/issue/{new_key}/transitions",
        headers=HEADERS,
        verify=JIRA_SSL
    )
    transitions = t_resp.json().get("transitions", [])
    transition_id = None
    for t in transitions:
        if "assign" in t["name"].lower():
            transition_id = t["id"]
            break

    if transition_id:
        requests.post(
            f"{JIRA_BASE_URL}/rest/api/2/issue/{new_key}/transitions",
            headers=HEADERS,
            json={"transition": {"id": transition_id}},
            verify=JIRA_SSL
        )
        print(f"✅ 狀態已轉為 In Progress")
    else:
        print(f"⚠️ 找不到 In Progress transition，可用的有：{[t['name'] for t in transitions]}")

    return new_key

def main():
    if len(sys.argv) < 2:
        print("用法：python3 create_qa_task.py TCG-148954 TCG-148947 ...")
        print("或直接輸入單號（空格分隔）：")
        user_input = input("> ").strip()
        tcg_keys = user_input.split()
    else:
        tcg_keys = sys.argv[1:]

    if not tcg_keys:
        print("❌ 請輸入至少一個 TCG 單號")
        return

    for tcg_key in tcg_keys:
        tcg_key = tcg_key.strip().upper()
        print(f"\n📋 處理 {tcg_key}...")
        try:
            summary, reporter = get_issue(tcg_key)
            versions = resolve_ped_icr_fix_versions()
            print(f"   原始 Summary：{summary}")
            print(f"   Fix Version：{[v['name'] for v in versions]}")
            print(f"   Reporter：{reporter}")

            new_key = create_qa_task(tcg_key, summary, reporter, fix_versions=versions)
            if new_key:
                print(f"   ✅ 建立成功：{new_key} → {qa_task_title(summary, 1)}")
                print(f"   🔗 {JIRA_BASE_URL}/browse/{new_key}")
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ API 錯誤：{e}")
        except Exception as e:
            print(f"   ❌ 發生錯誤：{e}")

if __name__ == "__main__":
    main()

