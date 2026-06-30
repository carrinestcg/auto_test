import requests
import urllib3
import os
import sys
from dotenv import load_dotenv
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============ 設定區 ============
JIRA_BASE_URL = "https://jira.tc-gaming.co/jira"
JIRA_TOKEN    = os.getenv("JIRA_TOKEN")
JIRA_SSL      = False

JIRA_USERNAME = "carrine.s"
WORKDAYS_FIELD = "customfield_11701"  # Workdays 欄位
# ================================

HEADERS = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_qa_tasks_by_tp(tp_key, assignee):
    """抓 Fix Version 開頭為 TP 單號 底下，指派給 assignee 的所有 QA Task"""
    jql = (
        f'fixVersion ~ "{tp_key}*" '
        f'AND assignee = "{assignee}" '
        f'AND issuetype = "QA Task" '
        f'ORDER BY created DESC'
    )

    payload = {
        "jql": jql,
        "maxResults": 100,
        "fields": ["summary", "status", WORKDAYS_FIELD, "created", "parent", "fixVersions"]
    }

    resp = requests.post(
        f"{JIRA_BASE_URL}/rest/api/2/search",
        headers=HEADERS,
        json=payload,
        verify=JIRA_SSL
    )
    resp.raise_for_status()
    issues = resp.json().get("issues", [])

    results = []
    for i in issues:
        f = i["fields"]
        workdays = f.get(WORKDAYS_FIELD)
        fix_version_names = [v["name"] for v in f.get("fixVersions", [])]
        results.append({
            "key": i["key"],
            "summary": f.get("summary", ""),
            "status": f.get("status", {}).get("name", ""),
            "workdays": float(workdays) if workdays else 0.0,
            "created": f.get("created", "")[:10],
            "parent": f.get("parent", {}).get("key", "") if f.get("parent") else "",
            "fix_versions": fix_version_names
        })
    return results

def build_report(tp_key, assignee, tasks):
    """組成可直接回傳給前端（或印出）的統計結果字典"""
    total_workdays = sum(t["workdays"] for t in tasks)
    by_status = {}
    for t in tasks:
        by_status.setdefault(t["status"], {"count": 0, "workdays": 0.0})
        by_status[t["status"]]["count"] += 1
        by_status[t["status"]]["workdays"] += t["workdays"]

    return {
        "tp_key": tp_key,
        "assignee": assignee,
        "total_count": len(tasks),
        "total_workdays": round(total_workdays, 2),
        "by_status": {
            status: {"count": d["count"], "workdays": round(d["workdays"], 2)}
            for status, d in by_status.items()
        },
        "tasks": tasks
    }

def print_report(report):
    """把 build_report 回傳的字典印到 terminal（CLI 模式用）"""
    print(f"\n{'='*60}")
    print(f"📊 {report['tp_key']} — QA Task 工作量統計（{report['assignee']}）")
    print(f"{'='*60}")
    print(f"總單數：{report['total_count']} 張")
    print(f"總耗時：{report['total_workdays']} workdays\n")

    print("依狀態分布：")
    for status, d in report["by_status"].items():
        print(f"   {status}：{d['count']} 張，{d['workdays']} workdays")

    print(f"\n{'─'*60}")
    print("明細：")
    for t in report["tasks"]:
        parent_info = f" (parent: {t['parent']})" if t["parent"] else ""
        print(f"   {t['key']} | {t['status']:12} | {t['workdays']:5.2f}天 | {t['created']} | {t['summary'][:30]}{parent_info}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        tp_key = input("請輸入 TP 單號（例如 TP-5229）：> ").strip().upper()
        assignee = input(f"請輸入 Jira 帳號（預設 {JIRA_USERNAME}）：> ").strip() or JIRA_USERNAME
    else:
        tp_key = sys.argv[1].strip().upper()
        assignee = sys.argv[2].strip() if len(sys.argv) > 2 else JIRA_USERNAME

    if not tp_key:
        print("❌ 請輸入 TP 單號")
        sys.exit(1)

    print(f"🔍 正在從 Jira 抓取 {tp_key} 底下的 QA Task...")
    try:
        tasks = fetch_qa_tasks_by_tp(tp_key, assignee)
        if not tasks:
            print(f"⚠️ 找不到 Fix Version 包含 {tp_key} 且指派給你的 QA Task")
        else:
            report = build_report(tp_key, assignee, tasks)
            print_report(report)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API 錯誤：{e}")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")