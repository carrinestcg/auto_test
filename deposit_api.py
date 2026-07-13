import requests,logging
from datetime import datetime,timedelta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def header(token,merchantCode):
    return{
        
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Authorization": token,
    "Connection": "keep-alive",
    "Language": "zh_CN",
    "Merchant": merchantCode,
    "Origin": "http://sit-admin2.tcg.com",
    "Referer": "http://sit-admin2.tcg.com/20000",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "environment": "TCG3",
    "merchantCode": merchantCode,
    "platform": "TCG"
    
    }
def get_token():
    login_url="http://sit-admin2.tcg.com/tac/api/login/password"
    payload={
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": "",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Merchant": "gi8viet",
        "MerchantCode": "gi8viet",
        "Origin": "http://sit-admin2.tcg.com",
        "Referer": "http://sit-admin2.tcg.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "environment": "",
        "language": "zh_CN",
        "noErrorNotice": "true",
        "platform": ""
    }
    
    cookies = {
        "language": "zh_CN"
    }
    requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
    token_data=requests_data.json()
    return token_data.get("token")


def deposit(token,merchantCode):
    API_URL = "http://sit-admin2.tcg.com/tac/api/relay/get/mcs-player-deposit-search" 
    start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
    end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")
    params={
        "username":"",
        "depositId":"",
        "bankRef":"",
        "depositStatus":"",
        "amountFromStr":"",
        "amountToStr":"",
        "depositType":"",
        "bankAcctIdList":"",
        "searchDateMode":"requestTime",
        "dateFrom":start_time,
        "dateTo":end_time,
        "tcpBankCode":"",
        "merchantCode":"gi8viet",
        "pageNo":1,
        "pageSize":1000

        }

    headers = header(token,merchantCode)
    cookies = {
        "language": "zh_CN"
    }
    try:
        response = requests.get(API_URL, headers=headers,params=params, cookies=cookies, verify=False)
        response.raise_for_status()
        
        
        response_data = response.json()
        
        
        if response_data.get('success') == True:
            logging.info(f"搜尋充值對象成功: ")
            depositId=response_data.get('value',[])
            filter_data=[d for d in depositId if d.get('depositStatus')=='N']
            logging.info(f"總共拿到 {len(depositId)} 個存款對象")
            return filter_data
            
        else:
            error_msg = response_data.get("message", "未知錯誤")
            logging.error(f"搜尋充值對象失敗: {error_msg}")
            return []
        
    except Exception as e:
        logging.error(f"狀態碼: {response.status_code}",e)
        return []
def approve_deposit(token,deposit_Info,merchantCode):
    try:
        API_URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-v3-deposit-processAndApprove"
        if deposit_Info.get("depositAmount") is None:
            logging.error(f"充值ID: {deposit_Info['depositId']} 缺少存款金額，無法處理")
            return False
        payload={
        
        "depositId": deposit_Info["depositId"],
        "tpRefNo": None,
        "payerBankAcctName": None,
        "payerBankAcctNum": None,
        "depositAmount": deposit_Info.get("depositAmount"),
        "bankRef":deposit_Info.get("bankRef"),
        "operatorRemark": None,
        "internalRemark": None,
        "version": 1,
        "merchantCode": "gi8viet",
        "isProcessAndApprove": True
        }
        headers = header(token,merchantCode)
        cookies = {
        "language": "zh_CN"
        }
        response=requests.post(API_URL, json=payload,cookies=cookies,verify=False, headers=headers)
        response_data = response.json()

        if response_data.get('success')==True:
            logging.info(f"成功批准ID: {deposit_Info['depositId']} , 金額: {deposit_Info['requestAmount']}")
            return True
        else:
            logging.info(f"未成功批准ID: {deposit_Info['depositId']}")
            return False
    except Exception as e:
        logging.error(f"處理充值 ID: {deposit_Info['depositId']} 時發生錯誤: {e}")
        return False
    
def batch_approve(merchantCode):
    logging.info("已進入 batch_approve 函數") 
    deposit_Info = None
    try:
        token=get_token()
        deposit_list=deposit(token,merchantCode)
        if not deposit_list:
            logging.info("沒有找到充值ID")
            return
        total_count=len(deposit_list)
        success_count=0
        fail_count=0

        for index, deposit_Info in enumerate(deposit_list,1):
            logging.info(f"正在處理第{index}/{total_count}的充值list,金額{deposit_Info['requestAmount']}")
            if approve_deposit(token,deposit_Info,merchantCode):
                success_count+=1
            else:
                fail_count+=1
        logging.info(f"批量處理充值完成")
        logging.info(f"總計: {total_count} 條記錄")
        logging.info(f"成功: {success_count} 條")
        logging.info(f"失敗: {fail_count} 條")

    except Exception as e:
        logging.error(f"處理充值 ID: {deposit_Info['depositId']} 時發生錯誤: {e}")
        return False

    

   