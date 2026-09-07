"""
掃描指定資料夾內所有 .py 檔案用到的 import,
並比對目前環境中哪些套件尚未安裝。

使用方式:
    python check_missing_packages.py /path/to/your/project

會印出:
  1. 專案中用到、但目前環境沒安裝的第三方套件名稱
  2. 一行可直接複製執行的 pip install 指令
"""

import ast
import importlib.util
import sys
from pathlib import Path

# 這些是 Python 標準函式庫自帶的模組,不需要另外安裝,直接略過
STDLIB_MODULES = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()

# import 名稱 -> 實際 pip 套件名稱 對照表(有些套件的 import 名稱跟 pip 安裝名稱不同)
IMPORT_TO_PIP_NAME = {
    "yaml": "pyyaml",
    "cv2": "opencv-python",
    "PIL": "pillow",
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "jwt": "pyjwt",
    "openpyxl": "openpyxl",
    "sklearn": "scikit-learn",
    "google": "google-api-python-client",
}

# 專案內部自己寫的模組(例如 Customer_id, DB_connect 等)不需要 pip 安裝,
# 這裡先蒐集專案裡所有 .py 檔案的檔名(不含副檔名),當作「本地模組」名單來排除
def collect_local_module_names(root: Path):
    names = set()
    for py_file in root.rglob("*.py"):
        names.add(py_file.stem)
    return names


def collect_imports_from_file(py_file: Path):
    imports = set()
    try:
        source = py_file.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(py_file))
    except (SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:  # 忽略 from . import xxx 這種相對匯入
                imports.add(node.module.split(".")[0])
    return imports


def is_installed(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python check_missing_packages.py /path/to/your/project")
        sys.exit(1)

    root = Path(sys.argv[1]).resolve()
    if not root.exists():
        print(f"找不到路徑: {root}")
        sys.exit(1)

    local_modules = collect_local_module_names(root)

    all_imports = set()
    for py_file in root.rglob("*.py"):
        all_imports |= collect_imports_from_file(py_file)

    # 排除標準函式庫 跟 專案內部自己的模組
    third_party_imports = {
        name for name in all_imports
        if name not in STDLIB_MODULES and name not in local_modules
    }

    missing = sorted(
        name for name in third_party_imports if not is_installed(name)
    )

    if not missing:
        print("✅ 目前環境已經安裝了所有偵測到的第三方套件,沒有缺漏。")
        return

    print("❌ 偵測到以下套件尚未安裝:\n")
    for name in missing:
        pip_name = IMPORT_TO_PIP_NAME.get(name, name)
        print(f"  - import {name}  →  pip install {pip_name}")

    pip_names = sorted({IMPORT_TO_PIP_NAME.get(name, name) for name in missing})
    print("\n可直接複製以下指令一次全部安裝:\n")
    print(f"  pip install {' '.join(pip_names)}")


if __name__ == "__main__":
    main()