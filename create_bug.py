import argparse
import sys

import requests
import urllib3

from create_qa_task import ASSIGNEE, HEADERS, JIRA_BASE_URL, JIRA_SSL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_ENVIRONMENT = "SIT"
DEFAULT_DEVICE = "HTML"
DEFAULT_PRIORITY = "High"

ENVIRONMENT_OPTIONS = {
    "DEV": "10500",
    "SIT": "10501",
    "UAT": "10502",
    "PROD": "10503",
    "STG": "10504",
}
DEVICE_OPTIONS = {
    "HTML": "10505",
    "iOS": "10506",
    "Android": "10507",
    "Application": "10508",
    "API": "10509",
}


TCG_PROJECT_ID = 10602


def search_fix_versions(query, limit=15):
    query = (query or "").strip()
    if len(query) < 2:
        return []
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/version",
        headers=HEADERS,
        params={"query": query, "maxResults": 50},
        verify=JIRA_SSL,
        timeout=20,
    )
    resp.raise_for_status()
    matches = []
    for version in resp.json().get("values") or []:
        if version.get("projectId") not in (TCG_PROJECT_ID, 10602):
            continue
        if version.get("archived"):
            continue
        matches.append({
            "id": version.get("id"),
            "name": version.get("name"),
            "released": bool(version.get("released")),
        })
        if len(matches) >= limit:
            break
    matches.sort(key=lambda item: (item["released"], (item["name"] or "").lower()))
    return matches


def search_issues(query, limit=20):
    query = (query or "").strip()
    if len(query) < 2:
        return []
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/issue/picker",
        headers=HEADERS,
        params={
            "query": query,
            "currentJQL": "project = TCG",
            "showSubTasks": "true",
            "showSubTaskParent": "true",
        },
        verify=JIRA_SSL,
        timeout=20,
    )
    resp.raise_for_status()
    matches = []
    for section in resp.json().get("sections") or []:
        group = section.get("sub") or section.get("label") or "Matching issues"
        for issue in section.get("issues") or []:
            key = issue.get("key") or ""
            if not key:
                continue
            matches.append({
                "id": issue.get("id") or key,
                "key": key,
                "name": key,
                "summary": issue.get("summaryText") or issue.get("summary") or "",
                "group": group,
            })
            if len(matches) >= limit:
                return matches
    return matches


def search_components(query, limit=15):
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/project/TCG/components",
        headers=HEADERS,
        verify=JIRA_SSL,
        timeout=20,
    )
    resp.raise_for_status()
    needle = (query or "").strip().lower()
    matches = []
    for component in resp.json() or []:
        name = component.get("name") or ""
        if needle and needle not in name.lower():
            continue
        matches.append({"id": component.get("id"), "name": name})
        if len(matches) >= limit:
            break
    return matches


def _split_names(value):
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = str(value or "").replace(";", ",").split(",")
    return [item.strip() for item in items if str(item).strip()]


def build_description(description, expected="", actual=""):
    text = (description or "").strip()
    if text and not text.lower().startswith("issue"):
        text = f"issue:\n\n{text}"
    if expected.strip():
        text = f"{text}\n\n預期結果：\n{expected.strip()}"
    if actual.strip():
        text = f"{text}\n\n實際結果：\n{actual.strip()}"
    return text


def _split_issue_keys(value):
    keys = []
    for item in _split_names(value):
        token = item.split()[0].strip().upper()
        if token:
            keys.append(token)
    return keys


def link_related_issues(new_key, related_keys, link_type="Relates"):
    errors = []
    for related_key in related_keys:
        resp = requests.post(
            f"{JIRA_BASE_URL}/rest/api/2/issueLink",
            headers=HEADERS,
            json={
                "type": {"name": link_type},
                "inwardIssue": {"key": new_key},
                "outwardIssue": {"key": related_key},
            },
            verify=JIRA_SSL,
            timeout=20,
        )
        if resp.status_code not in (200, 201, 204):
            errors.append(f"{related_key}: {resp.status_code} {resp.text}")
    return errors


def create_bug(
    summary,
    description,
    fix_version,
    component,
    environment=DEFAULT_ENVIRONMENT,
    device=DEFAULT_DEVICE,
    priority=DEFAULT_PRIORITY,
    expected="",
    actual="",
    related_key="",
    assignee=None,
):
    summary = (summary or "").strip()
    fix_versions = [{"name": name} for name in _split_names(fix_version)]
    components = [{"name": name} for name in _split_names(component)]
    if not summary:
        raise ValueError("請提供 Bug 標題")
    if not fix_versions:
        raise ValueError("請提供 Fix Version/s")
    if not components:
        raise ValueError("請提供 Component/s")

    env_key = (environment or DEFAULT_ENVIRONMENT).strip().upper()
    env_id = ENVIRONMENT_OPTIONS.get(env_key)
    if not env_id:
        raise ValueError(f"不支援的 Environment：{environment}，可用 {sorted(ENVIRONMENT_OPTIONS)}")

    device_key = (device or DEFAULT_DEVICE).strip()
    device_id = DEVICE_OPTIONS.get(device_key) or DEVICE_OPTIONS[DEFAULT_DEVICE]

    fields = {
        "project": {"key": "TCG"},
        "issuetype": {"name": "Bug"},
        "summary": summary,
        "description": build_description(description, expected, actual),
        "assignee": {"name": (assignee or ASSIGNEE).strip()},
        "priority": {"name": priority or DEFAULT_PRIORITY},
        "fixVersions": fix_versions,
        "components": components,
        "customfield_10700": {"id": env_id},
        "customfield_10701": [{"id": device_id}],
    }

    resp = requests.post(
        f"{JIRA_BASE_URL}/rest/api/2/issue",
        headers=HEADERS,
        json={"fields": fields},
        verify=JIRA_SSL,
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        print(f"❌ 建立失敗：{resp.status_code} {resp.text}")
        return None, resp.text

    new_key = resp.json().get("key")
    related_keys = _split_issue_keys(related_key)
    if new_key and related_keys:
        link_errors = link_related_issues(new_key, related_keys)
        if link_errors:
            return new_key, "建立成功，但關聯失敗：" + "；".join(link_errors)
    return new_key, None


def main():
    parser = argparse.ArgumentParser(description="建立 TCG Bug 單")
    parser.add_argument("--summary", required=True, help="Bug 標題")
    parser.add_argument("--fix-version", required=True, help="Fix Version/s，例如 TP-3946 排行榜功能2.0")
    parser.add_argument("--component", required=True, help="Component/s，例如 PCD Promotion")
    parser.add_argument("--description", default="", help="重現步驟")
    parser.add_argument("--expected", default="", help="預期結果")
    parser.add_argument("--actual", default="", help="實際結果")
    parser.add_argument("--env", default=DEFAULT_ENVIRONMENT, help="DEV/SIT/UAT/PROD/STG")
    parser.add_argument("--device", default=DEFAULT_DEVICE, help="HTML/iOS/Android/Application/API")
    parser.add_argument("--priority", default=DEFAULT_PRIORITY, help="High/Normal/Major/...")
    parser.add_argument("--related", default="", help="關聯單，例如 TCG-154103")
    args = parser.parse_args()

    try:
        new_key, error = create_bug(
            args.summary,
            args.description,
            args.fix_version,
            args.component,
            environment=args.env,
            device=args.device,
            priority=args.priority,
            expected=args.expected,
            actual=args.actual,
            related_key=args.related,
        )
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

    if not new_key:
        print(error or "建立失敗")
        sys.exit(1)
    print(f"✅ 建立成功：{new_key}")
    print(f"🔗 {JIRA_BASE_URL}/browse/{new_key}")
    if error:
        print(f"⚠️ {error}")


if __name__ == "__main__":
    main()
