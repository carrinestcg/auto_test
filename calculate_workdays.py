import re
import requests
import urllib3
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============ 設定區 ============
JIRA_BASE_URL = "https://jira.tc-gaming.co/jira"
JIRA_TOKEN    = os.getenv("JIRA_TOKEN")
JIRA_SSL      = False

JIRA_USERNAME = "carrine.s"
WORKDAYS_FIELD = "customfield_11701"  # Workdays 欄位
SEARCH_PAGE_SIZE = 100
SEARCH_MAX_PAGES = 10
# ================================

HEADERS = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Content-Type": "application/json"
}

_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ISSUE_CACHE = {}


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


def _normalize_tp(value):
    return re.sub(r"[^A-Z0-9]", "", (value or "").upper())


def _append_date_filter(jql, start_date=None, end_date=None):
    clauses = []
    start_date = normalize_date(start_date)
    end_date = normalize_date(end_date)
    if start_date:
        clauses.append(f'created >= "{start_date}"')
    if end_date:
        # Jira date equality is day-level; use next day with < for inclusive end date.
        end_exclusive = (
            datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")
        clauses.append(f'created < "{end_exclusive}"')
    if not clauses:
        return jql
    if "ORDER BY" in jql:
        base, order = jql.rsplit("ORDER BY", 1)
        return f"{base.strip()} AND {' AND '.join(clauses)} ORDER BY{order}"
    return f"{jql} AND {' AND '.join(clauses)}"


def _filter_tasks_by_date_range(tasks, start_date=None, end_date=None):
    """Python-side guard: enforce created date range even if JQL misses edge cases."""
    start_date = normalize_date(start_date)
    end_date = normalize_date(end_date)
    if not start_date and not end_date:
        return tasks

    filtered = []
    for task in tasks:
        created = normalize_date((task.get("created") or "")[:10])
        if not created:
            continue
        if start_date and created < start_date:
            continue
        if end_date and created > end_date:
            continue
        filtered.append(task)
    return filtered

def _jira_error_message(resp):
    try:
        body = resp.json()
        msgs = body.get("errorMessages") or []
        if msgs:
            return "; ".join(msgs)
        errors = body.get("errors") or {}
        if errors:
            return "; ".join(f"{k}: {v}" for k, v in errors.items())
    except ValueError:
        pass
    return resp.text[:300] or resp.reason


def _normalize_jira_user(value):
    return (value or "").strip().lower()


def _build_assignee_clause(assignee, include_reporter=False):
    assignee = (assignee or "").strip()
    if include_reporter:
        return f'(assignee = "{assignee}" OR reporter = "{assignee}")'
    return f'assignee = "{assignee}"'


def _task_is_assignee(task, assignee):
    return _normalize_jira_user(task.get("assignee")) == _normalize_jira_user(assignee)


def _task_is_reporter_only(task, assignee):
    user = _normalize_jira_user(assignee)
    if not user:
        return False
    reporter = _normalize_jira_user(task.get("reporter"))
    assignee_name = _normalize_jira_user(task.get("assignee"))
    return reporter == user and assignee_name != user


def _filter_tasks_for_user(tasks, assignee, include_reporter=False):
    if include_reporter:
        return tasks
    return [task for task in tasks if _task_is_assignee(task, assignee)]


def _build_qa_task_jql_queries(assignee, start_date=None, end_date=None, include_reporter=False):
    """Try multiple JQL shapes; some Jira setups differ on issuetype naming."""
    user_clause = _build_assignee_clause(assignee, include_reporter=include_reporter)
    base_queries = [
        f'{user_clause} AND issuetype = "QA Task" ORDER BY created DESC',
        f'{user_clause} AND summary ~ "\\\\[QA\\\\]" ORDER BY created DESC',
        f'{user_clause} AND text ~ "QA Task" ORDER BY created DESC',
        f'{user_clause} AND summary ~ "PED" AND summary ~ "測試" ORDER BY created DESC',
    ]
    return [_append_date_filter(q, start_date, end_date) for q in base_queries]


def _get_issue_fields(issue_key, fields):
    cache_key = (issue_key, tuple(fields))
    if cache_key in _ISSUE_CACHE:
        return _ISSUE_CACHE[cache_key]

    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}",
        headers=HEADERS,
        params={"fields": ",".join(fields)},
        verify=JIRA_SSL,
    )
    if not resp.ok:
        return None
    data = resp.json().get("fields") or {}
    _ISSUE_CACHE[cache_key] = data
    return data


def _extract_fix_versions(fields):
    if not fields:
        return []
    return [v.get("name", "") for v in fields.get("fixVersions") or [] if v.get("name")]


def _matches_tp_key(task, tp_key):
    prefix = _normalize_tp(tp_key)
    if not prefix:
        return True

    candidates = list(task.get("fix_versions") or [])
    parent_key = task.get("parent") or ""
    if parent_key:
        parent_fields = _get_issue_fields(parent_key, ["fixVersions", "summary"])
        candidates.extend(_extract_fix_versions(parent_fields))
        parent_summary = (parent_fields or {}).get("summary") or ""
        if _normalize_tp(parent_summary).find(prefix) >= 0:
            return True

    summary = task.get("summary") or ""
    if _normalize_tp(summary).find(prefix) >= 0:
        return True

    for name in candidates:
        normalized = _normalize_tp(name)
        if normalized.startswith(prefix) or prefix in normalized:
            return True
    return False


def fetch_qa_tasks_by_tp(tp_key, assignee, start_date=None, end_date=None, include_reporter=False):
    tasks = fetch_qa_tasks_by_assignee(
        assignee, start_date, end_date, include_reporter=include_reporter
    )
    return [t for t in tasks if _matches_tp_key(t, tp_key)]


def fetch_qa_tasks_by_assignee(assignee, start_date=None, end_date=None, include_reporter=False):
    """Fetch QA tasks for a user. Default: assignee only (excludes reporter-only tickets)."""
    merged = {}
    errors = []

    for jql in _build_qa_task_jql_queries(
        assignee, start_date, end_date, include_reporter=include_reporter
    ):
        try:
            for task in _search_qa_tasks(jql):
                merged[task["key"]] = task
        except requests.HTTPError as exc:
            errors.append(str(exc))

    if not merged and errors:
        raise requests.HTTPError(errors[0])

    tasks = list(merged.values())
    tasks = _filter_tasks_for_user(tasks, assignee, include_reporter=include_reporter)
    tasks = _filter_tasks_by_date_range(tasks, start_date, end_date)
    tasks.sort(key=lambda t: t.get("created", ""), reverse=True)
    return tasks


def _search_qa_tasks(jql):
    fields = ["summary", "status", WORKDAYS_FIELD, "created", "parent", "fixVersions", "assignee", "reporter"]
    results = []
    start_at = 0

    for _ in range(SEARCH_MAX_PAGES):
        payload = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": SEARCH_PAGE_SIZE,
            "fields": fields,
        }
        resp = requests.post(
            f"{JIRA_BASE_URL}/rest/api/2/search",
            headers=HEADERS,
            json=payload,
            verify=JIRA_SSL,
        )
        if not resp.ok:
            detail = _jira_error_message(resp)
            raise requests.HTTPError(
                f"{resp.status_code} Client Error: {detail} for url: {resp.url}",
                response=resp,
            )

        body = resp.json()
        issues = body.get("issues", [])
        if not issues:
            break

        for issue in issues:
            f = issue["fields"]
            workdays = f.get(WORKDAYS_FIELD)
            fix_version_names = _extract_fix_versions(f)
            parent = f.get("parent") or {}
            assignee_name = ((f.get("assignee") or {}).get("name") or "")
            reporter_name = ((f.get("reporter") or {}).get("name") or "")
            results.append({
                "key": issue["key"],
                "summary": f.get("summary", ""),
                "status": (f.get("status") or {}).get("name", ""),
                "workdays": float(workdays) if workdays else 0.0,
                "created": (f.get("created") or "")[:10],
                "parent": parent.get("key", "") if parent else "",
                "fix_versions": fix_version_names,
                "assignee": assignee_name,
                "reporter": reporter_name,
            })

        start_at += len(issues)
        total = body.get("total", 0)
        if start_at >= total:
            break

    return results

_DONE_TOKENS = ("done", "closed", "resolved")
def _is_done_status(status):
    tokens = re.split(r"[\s/_-]+", (status or "").lower())
    return any(t in _DONE_TOKENS for t in tokens if t)

def build_report(tp_key, assignee, tasks, start_date=None, end_date=None):
    total_workdays = sum(t["workdays"] for t in tasks)
    by_status = {}
    for t in tasks:
        by_status.setdefault(t["status"], {"count": 0, "workdays": 0.0})
        by_status[t["status"]]["count"] += 1
        by_status[t["status"]]["workdays"] += t["workdays"]
        
    done_count = sum(1 for t in tasks if _is_done_status(t["status"]))
    total = len(tasks)
    completion_rate = round(done_count / total * 100, 1) if total else 0.0
    
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
        "tasks": tasks,
        "done_count": done_count,
        "total": total,
        "completion_rate": completion_rate
    }


def print_report(report):
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
