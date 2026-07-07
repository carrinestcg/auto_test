import re
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

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def normalize_date(value):
    """Normalize optional date input to YYYY-MM-DD."""
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if _DATE_PATTERN.match(text):
        return text
    return ""


def _append_date_filter(jql, start_date=None, end_date=None):
    clauses = []
    start_date = normalize_date(start_date)
    end_date = normalize_date(end_date)
    if start_date:
        clauses.append(f'created >= "{start_date}"')
    if end_date:
        clauses.append(f'created <= "{end_date}"')
    if not clauses:
        return jql
    if "ORDER BY" in jql:
        base, order = jql.rsplit("ORDER BY", 1)
        return f"{base.strip()} AND {' AND '.join(clauses)} ORDER BY{order}"
    return f"{jql} AND {' AND '.join(clauses)}"


def fetch_qa_tasks_by_tp(tp_key, assignee, start_date=None, end_date=None):
    """抓 Fix Version 開頭為 TP 單號 底下，指派給 assignee 的所有 QA Task"""
    jql = (
        f'fixVersion ~ "{tp_key}*" '
        f'AND assignee = "{assignee}" '
        f'AND issuetype = "QA Task" '
        f'ORDER BY created DESC'
    )
    jql = _append_date_filter(jql, start_date, end_date)
    return _search_qa_tasks(jql)


def fetch_qa_tasks_by_assignee(assignee, start_date=None, end_date=None):
    """抓指派給 assignee 的所有 QA Task（不限 TP 單號）"""
    jql = (
        f'assignee = "{assignee}" '
        f'AND issuetype = "QA Task" '
        f'ORDER BY created DESC'
    )
    jql = _append_date_filter(jql, start_date, end_date)
    return _search_qa_tasks(jql)


def _search_qa_tasks(jql):
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


def build_report(tp_key, assignee, tasks, start_date=None, end_date=None):
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
        "date_from": normalize_date(start_date),
        "date_to": normalize_date(end_date),
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
    if report["tp_key"]:
        print(f"📊 {report['tp_key']} — QA Task 工作量統計（{report['assignee']}）")
    else:
        print(f"📊 {report['assignee']} — 全部 QA Task 工作量統計")
    if report.get("date_from") or report.get("date_to"):
        date_from = report.get("date_from") or "—"
        date_to = report.get("date_to") or "—"
        print(f"日期區間：{date_from} ~ {date_to}")
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
        tp_key = input("請輸入 TP 單號（留空則查該帳號全部 QA Task）：> ").strip().upper()
        assignee = input(f"請輸入 Jira 帳號（預設 {JIRA_USERNAME}）：> ").strip() or JIRA_USERNAME
        date_from = input("開始日期 YYYY-MM-DD（選填）：> ").strip()
        date_to = input("結束日期 YYYY-MM-DD（選填）：> ").strip()
    else:
        tp_key = sys.argv[1].strip().upper()
        assignee = sys.argv[2].strip() if len(sys.argv) > 2 else JIRA_USERNAME
        date_from = sys.argv[3].strip() if len(sys.argv) > 3 else ""
        date_to = sys.argv[4].strip() if len(sys.argv) > 4 else ""

    if not assignee:
        print("❌ 請輸入 Jira 帳號")
        sys.exit(1)

    date_from = normalize_date(date_from)
    date_to = normalize_date(date_to)
    if date_from and date_to and date_from > date_to:
        print("❌ 開始日期不能晚於結束日期")
        sys.exit(1)

    try:
        if tp_key:
            print(f"🔍 正在從 Jira 抓取 {tp_key} 底下的 QA Task...")
            tasks = fetch_qa_tasks_by_tp(tp_key, assignee, date_from, date_to)
        else:
            print(f"🔍 正在從 Jira 抓取 {assignee} 的全部 QA Task...")
            tasks = fetch_qa_tasks_by_assignee(assignee, date_from, date_to)

        if not tasks:
            print("⚠️ 找不到符合條件的 QA Task")
        else:
            report = build_report(tp_key, assignee, tasks, date_from, date_to)
            print_report(report)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API 錯誤：{e}")
    except Exception as e:
        print(f"❌ 發生錯誤：{e}")
