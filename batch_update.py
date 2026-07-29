import logging
import os
from datetime import datetime

import requests
import urllib3
from dotenv import load_dotenv

import jira_drive_comment

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEST_REPO_URL = os.getenv("TEST_REPO_URL", "http://10.81.1.49:9999").rstrip("/")
TEST_REPO_USERNAME = os.getenv("TEST_REPO_USERNAME", "carrine")
TEST_REPO_PASSWORD = os.getenv("TEST_REPO_PASSWORD", "")
TEST_REPO_TEAM_ID = os.getenv("TEST_REPO_TEAM_ID", "3")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _repo_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Origin": TEST_REPO_URL,
        "Referer": f"{TEST_REPO_URL}/test-run-execution",
        "Content-Type": "application/json",
    }


def login():
    if not TEST_REPO_PASSWORD:
        raise ValueError("請在 .env 設定 TEST_REPO_PASSWORD")

    url = f"{TEST_REPO_URL}/api/auth/login"
    payload = {
        "username_or_email": TEST_REPO_USERNAME,
        "remember_me": False,
        "password": TEST_REPO_PASSWORD,
    }
    response = requests.post(url, json=payload, verify=False, timeout=30)
    if response.status_code != 200:
        raise requests.HTTPError(
            f"測試平台登入失敗 ({response.status_code}): {response.text[:300]}"
        )

    access_token = response.json().get("access_token")
    if not access_token:
        raise ValueError("測試平台登入成功但未取得 access_token")
    logging.info("測試平台登入成功")
    return access_token


def get_test_run_config_id(access_token, test_run_name):
    test_run_name = str(test_run_name or "").strip()
    if not test_run_name:
        return None

    url = f"{TEST_REPO_URL}/api/teams/{TEST_REPO_TEAM_ID}/test-run-sets/overview"
    response = requests.get(
        url,
        headers=_repo_headers(access_token),
        params={"include_archived": "true", "limit": 10000},
        verify=False,
        timeout=60,
    )
    response.raise_for_status()

    for bucket in ("unassigned", "assigned", "archived"):
        for item in response.json().get(bucket) or []:
            name = (item.get("name") or "").strip()
            if name == test_run_name or test_run_name in name:
                config_id = item.get("id")
                logging.info("找到 test run %s -> config_id=%s", name, config_id)
                return config_id

    return None


def get_test_items(access_token, config_id):
    url = f"{TEST_REPO_URL}/api/teams/{TEST_REPO_TEAM_ID}/test-run-configs/{config_id}/items/"
    response = requests.get(
        url,
        headers=_repo_headers(access_token),
        params={"limit": 10000},
        verify=False,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        return data
    return data.get("results") or data.get("items") or []


def update_test_item(access_token, config_id, item_id, comment, assignee_name, test_result):
    url = (
        f"{TEST_REPO_URL}/api/teams/{TEST_REPO_TEAM_ID}/test-run-configs/"
        f"{config_id}/items/batch-update-results"
    )
    payload = {
        "updates": [
            {
                "id": item_id,
                "assignee_name": assignee_name,
                "test_result": test_result,
                "executed_at": datetime.now().isoformat(),
                "comment": comment,
            }
        ]
    }
    response = requests.post(
        url,
        headers=_repo_headers(access_token),
        json=payload,
        verify=False,
        timeout=60,
    )
    if response.status_code != 200:
        raise requests.HTTPError(
            f"更新失敗 item={item_id} ({response.status_code}): {response.text[:300]}"
        )
    return response.json()


def _apply_drive_links_to_test_run(
    scan_keys,
    direct,
    parent_alias,
    test_run_name,
    assignee_name,
    test_result,
    source_meta=None,
):
    access_token = login()
    config_id = get_test_run_config_id(access_token, test_run_name)
    if not config_id:
        raise ValueError(f"找不到測試 run：{test_run_name}")

    items = get_test_items(access_token, config_id)
    if not items:
        raise ValueError(f"test run {test_run_name} 底下沒有 test items")

    updated = []
    skipped = []

    for item in items:
        item_id = item.get("id")
        drive_link, matched_key = jira_drive_comment.pick_drive_link_for_item(
            item, direct, parent_alias
        )
        item_label = (
            item.get("name")
            or item.get("title")
            or item.get("summary")
            or str(item_id)
        )

        if not drive_link:
            skipped.append(
                {
                    "item_id": item_id,
                    "item_label": item_label,
                    "reason": "找不到對應 Jira 單號或 QA verified pass Drive 連結",
                }
            )
            continue

        update_test_item(
            access_token,
            config_id,
            item_id,
            drive_link,
            assignee_name,
            test_result,
        )
        updated.append(
            {
                "item_id": item_id,
                "item_label": item_label,
                "jira_key": matched_key,
                "comment": drive_link,
            }
        )

    if not updated:
        raise ValueError(
            "雖找到 Jira Drive 連結，但沒有任何 test item 能對應更新。"
            "請確認 test item 名稱/欄位含有 TCG 單號。"
        )

    result = {
        "test_run_name": test_run_name,
        "config_id": config_id,
        "scanned_issues": scan_keys,
        "drive_links": {**direct, **{f"{k} (parent)": v for k, v in parent_alias.items()}},
        "updated": updated,
        "skipped": skipped,
    }
    if source_meta:
        result.update(source_meta)
    return result


def run_batch_update_from_jira(
    ticket_key,
    test_run_name=None,
    assignee_name="Carrine Shih",
    test_result="Passed",
):
    ticket_key = jira_drive_comment.parse_ticket_key(ticket_key)
    if not ticket_key:
        raise ValueError("請提供有效的 TP 或 TCG 單號")

    test_run_name = (test_run_name or ticket_key).strip()
    scan_keys = jira_drive_comment.resolve_scan_keys(ticket_key)
    if not scan_keys:
        raise ValueError(f"無法解析 Jira 單號：{ticket_key}")

    direct, parent_alias = jira_drive_comment.build_drive_link_maps(scan_keys)
    if not direct and not parent_alias:
        raise ValueError(
            f"在 {ticket_key} 相關單號的 comment 中，找不到含 "
            f"'QA verified pass' 的 Google Drive 連結"
        )

    return _apply_drive_links_to_test_run(
        scan_keys,
        direct,
        parent_alias,
        test_run_name,
        assignee_name,
        test_result,
        source_meta={
            "source": "jira_ticket",
            "ticket_key": ticket_key,
        },
    )


def main(ticket_key, test_run_name=None):
    result = run_batch_update_from_jira(ticket_key, test_run_name=test_run_name)
    logging.info(
        "完成：更新 %s 筆，略過 %s 筆",
        len(result["updated"]),
        len(result["skipped"]),
    )
    return result


if __name__ == "__main__":
    import sys

    key = sys.argv[1] if len(sys.argv) > 1 else input("TP / TCG 單號：").strip()
    run_name = sys.argv[2] if len(sys.argv) > 2 else key
    main(key, run_name)
