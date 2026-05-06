import requests
import logging
import time
from datetime import datetime
import traceback
import random
import oracledb
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class Frontend:
    def __init__(self):
        self.session=requests.Session()
        self.userid=''
        self.customer_id=''
        
    def DB_connect(self,SQL):
        host="10.80.1.11"
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
    def get_Ticket_transaction_ID(self,merchantCode,username):
        tickets=[]
        '''
        current_time=datetime.now()
        unit_time=str(int(current_time.timestamp()*1000))
        '''
        login_URL="http://10.80.1.20:7001/promo-fe/resources/ticket/list"
        parmas={
            
            "status":"AVAILABLE",
            "isAll":"N",
            
        }
        self.customer_id=self.DB_connect(f"SELECT CUSTOMER_ID FROM TCG_CORE.US_CUSTOMER WHERE CUSTOMER_NAME='gi8viet@{username}'")
        headers={
            'Content-Type': 'application/json',
            'Merchant': merchantCode,
            'Language':"CN",
            'CustomerId':self.customer_id
        }
        
        response=self.session.get(login_URL,headers=headers,params=parmas, verify=False)
        response_json=response.json()
        
        if response_json.get('success'):
            self.response_value_list=response_json.get('value',[])

            if self.response_value_list:
                for item in self.response_value_list:
                    Trans_id=item.get('transactionId') 
                    if Trans_id:
                        tickets.append(Trans_id)
                logging.info(f"總共可領{len(tickets)}張")
                return tickets

        else:
            logging.error("交易ID查詢失敗")
            
        
        
    def approve_to_receive_ticket(self,trans_id):
        
        login_URL="http://10.80.1.20:7001/promo-fe/resources/ticket/claim"
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        headers={
            'Content-Type': 'application/json',
            'Merchant': self.merchantCode,
            'Connection': 'keep-alive',
            'Language': 'CN',
            'CustomerId':self.customer_id,
            "CustomerIP":CustomerIP
            
        }
        payload={
                "transactionId": trans_id,
                "isApp": "N"
        }

        
        response=self.session.post(login_URL,headers=headers,json=payload)
        response.raise_for_status()
        response_json=response.json()
        print(response_json)
        if response_json.get('success'):
            self.response_value_list=response_json.get('value',{})
            if self.response_value_list:
                Type=self.response_value_list.get('type') 
                logging.info(f"成功領取票卷 交易ID: {trans_id} 類別{Type}")
            return True
            
        else:
            logging.error("領取票卷失敗")
            logging.error(traceback.format_exc())
            return False
    def poccess_all_ticket(self,merchantCode,username,max_workers=10):
        self.merchantCode=merchantCode
        ticket=self.get_Ticket_transaction_ID(merchantCode,username)
        def claim(trans_id):
            return self.approve_to_receive_ticket(trans_id)
        result=[]
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures=[executor.submit(claim,tid) for tid in ticket]
            for future in as_completed(futures):
                result.append(future.result())
        logging.info(f"成功 {sum(result)} / {len(result)}")

def main(username,merchantCode):
    
    if not username:
        logging.info("no UserName")
        return False
    #填入玩家帳號
    

    try:    
        frontend = Frontend()
        frontend.poccess_all_ticket(merchantCode,username)
        

        
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")
            logging.error(traceback.format_exc())
