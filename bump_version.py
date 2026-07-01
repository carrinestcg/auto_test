#!/usr/bin/env python3
"""Release helper: auto-bump semver, write changelog, create git tag.

Usage:
  python3 bump_version.py "修正定時任務日期格式"
  python3 bump_version.py --minor "新增某某腳本"
  python3 bump_version.py --major "大改版"
  python3 bump_version.py --version 2.0.0 "指定版本號"

Version shown in the UI is read from the latest git tag at runtime.
version.json only needs changelog entries (version field is synced here).
"""

from __future__ import annotations

import argparse
import sys

from version_util import (
    bump_version,
    create_git_tag,
    resolve_current_version,
    write_changelog_entry,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump auto_test version via git tag")
    parser.add_argument(
        "items",
        nargs="*",
        help="Changelog bullet(s). If omitted, uses a generic release note.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--major", action="store_true", help="Bump major version")
    group.add_argument("--minor", action="store_true", help="Bump minor version")
    group.add_argument(
        "--version",
        dest="explicit_version",
        help="Use this version instead of auto bump (e.g. 2.0.0)",
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Only update version.json changelog, do not create git tag",
    )
    args = parser.parse_args()

    current = resolve_current_version()
    if args.explicit_version:
        new_version = args.explicit_version.lstrip("v")
    else:
        new_version = bump_version(current, major=args.major, minor=args.minor)

    items = list(args.items) or [f"Release v{new_version}"]
    write_changelog_entry(new_version, items)

    print(f"Current: v{current} -> New: v{new_version}")
    for line in items:
        print(f"  - {line}")

    if args.no_tag:
        print("Skipped git tag (--no-tag).")
        return

    message = f"v{new_version}\n\n" + "\n".join(f"- {line}" for line in items)
    if create_git_tag(new_version, message):
        print(f"Created git tag v{new_version}")
        print("Push with: git push origin v" + new_version)
    else:
        print(f"Git tag v{new_version} already exists or git tag failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
