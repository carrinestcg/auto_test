import requests
import logging
import oracledb
from datetime import datetime
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def Change_Password(customer_id:str):
    URL="http://10.81.1.22:7001/tcg-uss-ae/password"

    header={
        "Content-Type":"application/json"
    }
    payload={ 
        "customerId": customer_id, 
        "needLogInToChangePassword": True, 
        "password": "123qwe"
        }
    resposne=requests.put(URL,headers=header,json=payload,verify=False)
    resposne_json=resposne.json()
    if resposne_json.get("success"):
        logging.info("更改密碼完成")
        return True
    else:
        logging.error(f"更改失敗{resposne.text}")
        return False

def DB_connect(SQL):
    host="10.81.1.11"
    port = 1521              
    service_name = "tcgsit"
    username = "TCG_MCSDB"
    password = "Jv7UrDc7rsqJ87Km"

    dsn=f"{host}:{port}/{service_name}"

    conn=oracledb.connect(
        user=username,
        password=password,
        dsn=dsn
    )
    cursor=conn.cursor()
    cursor.execute(f"{SQL}")
    rows=cursor.fetchall()
    try:
        if rows:
            colums=[]
            for desc in cursor.description:
                colums.append(desc[0])
            for row in rows:
                print("="*60)
                print("資訊")
                print("="*60)
                for col,val in zip(colums,row):
                    if isinstance(val,datetime):
                        val_str=val.strftime('%Y-%m-%d %H:%M:%S')
                    elif val==" ":
                        val_str='(空白)'
                        
                    elif val is None:
                        val_str='NULL'
                        
                    else:
                        val_str=str(val)
                    
                    print(f"{col:25s}: {val_str}")
                    
        else:
            logging.info("查無資料")
        return str(rows[0][0])
            
    except oracledb.DatabaseError as e:
        logging.error(f"❌ 資料庫錯誤: {e}")
    except Exception as e:
        logging.error(f"❌ 未預期的錯誤: {str(e)}")
    finally:
        if cursor in locals() and cursor:
            cursor.close()
        if conn in locals() and conn:
            conn.close()
        
def main(username,platform):
    customer_id=DB_connect(f"SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='{platform}@{username}'")
    if not customer_id:
        logging.error("沒有拿到customer_id")
    isSuccess=Change_Password(customer_id)
    return isSuccess


    

