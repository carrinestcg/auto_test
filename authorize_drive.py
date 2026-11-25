"""讓 Drive 資料夾擁有者登入一次，之後上傳都用這次留下的授權。"""

from qa_jira_fill import authorize_drive

if __name__ == "__main__":
    path = authorize_drive()
    print(f"授權已儲存：{path}")
    print("請用資料夾擁有者登入。若 Flask 跑在另一台機器，把這個檔拷到那台的專案目錄後重開。")
