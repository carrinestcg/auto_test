"""Fetch Google Drive links from Jira comments containing 'QA verified pass'."""

import re
import requests
import urllib3
import os
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://jira.tc-gaming.co/jira")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_SSL = False

HEADERS = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Content-Type": "application/json",
}

JIRA_KEY_RE = re.compile(r"\b(TP|TCG|THD)-\d+\b", re.IGNORECASE)
QA_VERIFIED_RE = re.compile(r"qa\s*verified\s*pass", re.IGNORECASE)
DRIVE_URL_RE = re.compile(
    r"https?://(?:drive\.google\.com|docs\.google\.com)[^\s<>\"'\|\]\)]+",
    re.IGNORECASE,
)

SEARCH_PAGE_SIZE = 50
SEARCH_MAX_PAGES = 10
MAX_SCAN_KEYS = 200


def parse_ticket_key(raw):
    text = str(raw or "").strip().upper()
    if not text:
        return ""
    if JIRA_KEY_RE.fullmatch(text):
        return text
    match = JIRA_KEY_RE.search(text)
    return match.group(0).upper() if match else ""


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


def _adf_to_text(node):
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(item) for item in node)
    if not isinstance(node, dict):
        return str(node)
    if node.get("type") == "text":
        return node.get("text") or ""
    return "".join(_adf_to_text(child) for child in (node.get("content") or []))


def plain_comment_body(body):
    if body is None:
        return ""
    if isinstance(body, dict):
        return _adf_to_text(body)
    return str(body)


def _normalize_drive_url(url):
    return (url or "").rstrip(".,;)")


def fetch_comments(issue_key):
    comments = []
    start_at = 0

    while True:
        resp = requests.get(
            f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}/comment",
            headers=HEADERS,
            params={"startAt": start_at, "maxResults": 50, "orderBy": "created"},
            verify=JIRA_SSL,
        )
        if not resp.ok:
            detail = _jira_error_message(resp)
            raise requests.HTTPError(
                f"{resp.status_code} Client Error: {detail} for url: {resp.url}",
                response=resp,
            )

        body = resp.json()
        page = body.get("comments") or []
        comments.extend(page)
        total = body.get("total", len(comments))
        start_at += len(page)
        if start_at >= total or not page:
            break

    return comments


def find_qa_verified_drive_link(issue_key):
    """Return the Drive URL from the newest comment containing 'QA verified pass'."""
    for comment in reversed(fetch_comments(issue_key)):
        body = plain_comment_body(comment.get("body"))
        if not QA_VERIFIED_RE.search(body):
            continue
        urls = DRIVE_URL_RE.findall(body)
        if urls:
            return _normalize_drive_url(urls[0])
    return None


def get_issue_parent_key(issue_key):
    resp = requests.get(
        f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}",
        headers=HEADERS,
        params={"fields": "parent,subtasks,issuelinks"},
        verify=JIRA_SSL,
    )
    if not resp.ok:
        return None, [], []

    fields = resp.json().get("fields") or {}
    parent = fields.get("parent") or {}
    parent_key = parent.get("key")
    subtasks = [s.get("key") for s in (fields.get("subtasks") or []) if s.get("key")]

    linked = []
    for link in fields.get("issuelinks") or []:
        for side in ("inwardIssue", "outwardIssue"):
            issue = link.get(side)
            if issue and issue.get("key"):
                linked.append(issue["key"])

    return parent_key, subtasks, linked


def _jira_search(jql, fields=None):
    fields = fields or ["key"]
    issues = []
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
        page = body.get("issues") or []
        issues.extend(page)
        start_at += len(page)
        total = body.get("total", len(issues))
        if start_at >= total or not page:
            break

    return issues


def _search_related_issue_keys(ticket_key):
    prefix = re.sub(r"[^A-Z0-9]", "", ticket_key.upper())
    jql_candidates = [
        f"issue = {ticket_key}",
        f"parent = {ticket_key}",
        f"key = {ticket_key} OR parent = {ticket_key}",
        f'summary ~ "{ticket_key}" OR text ~ "{ticket_key}"',
        f'summary ~ "{prefix}" OR text ~ "{prefix}"',
    ]

    merged = []
    seen = set()
    errors = []

    for jql in jql_candidates:
        try:
            for issue in _jira_search(jql, fields=["key", "summary"]):
                key = issue.get("key")
                if key and key not in seen:
                    seen.add(key)
                    merged.append(key)
        except requests.HTTPError as exc:
            errors.append(str(exc))

    if not merged and errors:
        raise requests.HTTPError(errors[0])

    return merged


def resolve_scan_keys(ticket_key):
    """Collect Jira issue keys whose comments should be scanned."""
    ticket_key = parse_ticket_key(ticket_key)
    if not ticket_key:
        return []

    keys = []
    seen = set()

    def add(key):
        if not key or key in seen:
            return
        seen.add(key)
        keys.append(key)

    add(ticket_key)

    for key in _search_related_issue_keys(ticket_key):
        add(key)

    expanded = list(keys)
    for key in expanded:
        if len(keys) >= MAX_SCAN_KEYS:
            break
        _, subtasks, linked = get_issue_parent_key(key)
        for child in subtasks + linked:
            add(child)
            if len(keys) >= MAX_SCAN_KEYS:
                break

    return keys[:MAX_SCAN_KEYS]


def build_drive_link_maps(scan_keys):
    """
    Returns:
        direct: {issue_key: drive_url}
        parent_alias: {parent_issue_key: drive_url}  # QA subtask comment -> parent TCG
    """
    direct = {}
    parent_alias = {}

    for key in scan_keys:
        link = find_qa_verified_drive_link(key)
        if not link:
            continue
        direct[key] = link
        parent_key, _, _ = get_issue_parent_key(key)
        if parent_key:
            parent_alias[parent_key] = link

    return direct, parent_alias


def extract_issue_keys_from_text(*values):
    found = []
    seen = set()
    for value in values:
        if value is None:
            continue
        for match in JIRA_KEY_RE.finditer(str(value)):
            key = match.group(0).upper()
            if key not in seen:
                seen.add(key)
                found.append(key)
    return found


def pick_drive_link_for_item(item, direct, parent_alias):
    """Match a test-repo item to a Drive URL found in Jira comments."""
    if not item:
        return None, None

    candidate_fields = (
        "external_key",
        "jira_key",
        "reference",
        "case_id",
        "external_id",
        "name",
        "title",
        "summary",
        "description",
        "test_case_name",
        "test_case_title",
    )
    values = [item.get(field) for field in candidate_fields if item.get(field) is not None]
    issue_keys = extract_issue_keys_from_text(*values)

    for key in issue_keys:
        if key in direct:
            return direct[key], key
        if key in parent_alias:
            return parent_alias[key], key

    return None, None
