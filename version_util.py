"""Resolve app version from git tags, with version.json for changelog."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "version.json"
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _run_git(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return (result.stdout or "").strip() or None


def normalize_version(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = raw.strip().lstrip("v").split("-")[0]
    if SEMVER_RE.fullmatch(cleaned):
        return cleaned
    return None


def parse_version(raw: str | None) -> tuple[int, int, int] | None:
    normalized = normalize_version(raw)
    if not normalized:
        return None
    major, minor, patch = normalized.split(".")
    return int(major), int(minor), int(patch)


def format_version(parts: tuple[int, int, int]) -> str:
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def get_git_tag_version() -> str | None:
    for args in (
        ("describe", "--tags", "--abbrev=0", "--match", "v*"),
        ("describe", "--tags", "--abbrev=0", "--match", "[0-9]*"),
        ("describe", "--tags", "--abbrev=0"),
    ):
        raw = _run_git(*args)
        normalized = normalize_version(raw)
        if normalized:
            return normalized
    return None


def get_tag_release_date(tag_version: str) -> str | None:
    for tag_name in (f"v{tag_version}", tag_version):
        raw = _run_git("log", "-1", "--format=%cs", tag_name)
        if raw and re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            return raw
    return None


def _read_version_json() -> dict:
    try:
        with open(VERSION_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("version", "0.0.0")
    data.setdefault("released_at", "")
    data.setdefault("changelog", [])
    return data


def resolve_current_version() -> str:
    git_version = get_git_tag_version()
    if git_version:
        return git_version
    file_version = normalize_version(_read_version_json().get("version"))
    return file_version or "0.0.0"


def bump_version(
    current: str,
    *,
    major: bool = False,
    minor: bool = False,
) -> str:
    parts = parse_version(current) or (0, 0, 0)
    if major:
        return format_version((parts[0] + 1, 0, 0))
    if minor:
        return format_version((parts[0], parts[1] + 1, 0))
    return format_version((parts[0], parts[1], parts[2] + 1))


def load_version_info() -> dict:
    data = _read_version_json()
    git_version = get_git_tag_version()
    if git_version:
        data["version"] = git_version
        tag_date = get_tag_release_date(git_version)
        if tag_date:
            data["released_at"] = tag_date
    else:
        data["version"] = resolve_current_version()
    return data


def write_changelog_entry(version: str, items: list[str], release_date: str | None = None) -> dict:
    data = _read_version_json()
    release_date = release_date or date.today().isoformat()
    changelog = data.get("changelog") or []

    entry = {"version": version, "date": release_date, "items": items}
    if changelog and changelog[0].get("version") == version:
        changelog[0] = entry
    else:
        changelog.insert(0, entry)

    data["changelog"] = changelog
    data["version"] = version
    data["released_at"] = release_date
    VERSION_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data


def create_git_tag(version: str, message: str) -> bool:
    tag_name = f"v{version}"
    if _run_git("rev-parse", "--verify", f"refs/tags/{tag_name}"):
        return False
    result = subprocess.run(
        ["git", "-C", str(ROOT), "tag", "-a", tag_name, "-m", message],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return result.returncode == 0
