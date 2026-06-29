import requests
import urllib3
import sys
import os
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
    fix_versions = [{"name": v["name"]} for v in fields.get("fixVersions", [])]
    reporter    = fields.get("reporter", {}).get("name", ASSIGNEE)
    return summary, fix_versions, reporter

def create_qa_task(tcg_key, summary, fix_versions, reporter):
    """在 TCG 單底下建立 QA Task subtask，建立後轉為 In Progress"""
    new_summary = f"[QA][PED] 測試 {summary}"

    fields = {
            "project": {"key": "TCG"},
            "parent": {"key": tcg_key},
            "summary": new_summary,
            "issuetype": {"name": "QA Task"},
            "assignee": {"name": reporter},
            "fixVersions": fix_versions,
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
            summary, fix_versions, reporter = get_issue(tcg_key)
            print(f"   原始 Summary：{summary}")
            print(f"   Fix Version：{[v['name'] for v in fix_versions]}")
            print(f"   Reporter：{reporter}")

            new_key = create_qa_task(tcg_key, summary, fix_versions, reporter)
            if new_key:
                print(f"   ✅ 建立成功：{new_key} → [QA][PED] 測試 {summary}")
                print(f"   🔗 {JIRA_BASE_URL}/browse/{new_key}")
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ API 錯誤：{e}")
        except Exception as e:
            print(f"   ❌ 發生錯誤：{e}")

if __name__ == "__main__":
    main()

