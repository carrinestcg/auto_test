from flask import Flask,render_template,request,jsonify,Response,json
import MANUAL_SINGLE
import MANUAL_BATCH
import PROMOCODE_BATCH
import FRONTEND_DEPOSIT
import MANUAL_SIGN
import NEW_REGISTER_API
import Customer_id
import auto_create_ticket
import Manual_create_single_with_confirm
import SameTimeLogin_manager
import SIGLE_PROMO_7_TICKET
import PLAYER_RANK
import Condition_create_bonus
import ALL_deposit_promotion
import Frontend_receive_reward
import Frontend_receive_ticket
import App_download_API
import Change_password
import Lott_bet_without_main
import Compensation_api
import PostCard_Code
import test_manual_bonus
import pytest
from Create_member_Account import async_create_main
from deposit_api import batch_approve
import pandas as pd
import logging
import threading
import asyncio
import subprocess
import sys
import Extra_Reward
import test_Extra_bonus


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
python_flask=Flask(__name__)

@python_flask.route("/")
def hello():
    return render_template("index.html")
def auto_create_member_player(platform_type,username,amount):
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                try:
                    result =asyncio.run(async_create_main(platform,username,amount))
                    if isinstance(result, tuple) and len(result) == 2:
                        return result
                    else:
                        return 0,None
                except Exception as e:
                    logging.error(f"創建玩家 {username} 發生錯誤: {e}")
                    return 0,None
        return 0, None
def auto_create_player(platform_type,username):
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                try:
                    result =NEW_REGISTER_API.main(platform,username)
                    if isinstance(result, tuple) and len(result) == 2:
                        return result
                    else:
                        return 0,None
                except Exception as e:
                    logging.error(f"創建玩家 {username} 發生錯誤: {e}")
                    return 0,None
        return 0, None

def batch_approve_func(deposit_platform_type):
        for platform in deposit_platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                batch_approve(platform)

def manual_create_bonus(username,platform_type,promotion,ticket_id,amount):
        print(platform_type)
        for platform in platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                Manual_create_single_with_confirm.main(username,promotion,ticket_id,platform,amount)

def manual_create_7_type_tcket(username,promotion,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                SIGLE_PROMO_7_TICKET.main(username,promotion,platform)

def auto_create_ticket_func(ticket_type,ticket_input,platform_type):
    for platform in platform_type:
        if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
            for ticket in ticket_type:
                if ticket in ['CASH','FREE_SPIN','TEMU']:

                    ticket_name=f"{ticket_input}_{ticket}"
                    localizations = [
                            {
                                "language": "CN",
                                "name": ticket_name,
                                "description": None,
                                "lossMessage": None,
                                "imageUrl": None,
                                "imageName": None
                            }
                        ]
                    auto_create_ticket.main(ticket,localizations,platform)
                elif ticket in ['RAFFLE','GOLDEN_EGG' ,'WHEEL','GIFT']:
                    ticket_name=f"{ticket_input}_{ticket}"
                    localizations = [
                            {
                                "language": "CN",
                                "name": ticket_name,
                                "description": None,
                                "lossMessage": "loss",
                                "imageUrl": None,
                                "imageName": None
                            }
                        ]
                    auto_create_ticket.main(ticket,localizations,platform)

def frontend_receive_reward(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                Frontend_receive_reward.main(username,platform)

def frontend_receive_ticket(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                Frontend_receive_ticket.main(username,platform)

def get_customer_data(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                customer_detail=Customer_id.main(username,platform)
                return customer_detail
        return None,None,None
        
def trigger_APP_download_API(platform_type,username):
        print(platform_type)
        for platform in platform_type:
            if platform in  ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                result=App_download_API.main(platform,username)
                return result
isSuccess = False
def trigger_change_password_API(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet','jkdscus1'):
                isSuccess=Change_password.main(username,platform)
        return isSuccess
 
def lottery_bet(username,amount):
        Lott_bet_without_main.implement(username,amount)
        
@python_flask.route('/api/PROMOCODE_BATCH',methods=['POST']) #APP下載獎勵API
def api_PROMOCODE_BATCH():
    data=request.json
    username=data["username"]
    isSuccess=PROMOCODE_BATCH.main(username)
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "Success Received PromoCode"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "Receive PromoCode Failed"
                }
            ),400
@python_flask.route('/api/SameTimeLogin',methods=['POST']) #APP下載獎勵API
def api_SameTimeLogin():
    isSuccess=SameTimeLogin_manager.main()
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "SameTimeLogin Success"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "SameTimeLogin Failed"
                }
            ),400
@python_flask.route('/api/PLAYER_RANK',methods=['POST']) #APP下載獎勵API
def api_PLAYER_RANK():
    data=request.json
    username=data["username"]
    isSuccess=PLAYER_RANK.main(username)
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "Success Received PromoCode"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "Receive PromoCode Failed"
                }
            ),400
@python_flask.route('/api/Codition_create_bonus',methods=['POST']) #APP下載獎勵API
def api_Codition_create_bonus():
    isSuccess=Condition_create_bonus.main()
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "Success Received PromoCode"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "Receive PromoCode Failed"
                }
            ),400

@python_flask.route('/api/APP_Download',methods=['POST']) #APP下載獎勵API
def api_app_download():
    data=request.get_json(silent=True)
    if not data:
        return jsonify(
        {
            "success": False,
            "message": "Triiger API Failed"
            }
        ),400
        
    username=data["username"]
    platforms=data["platforms"]  
    result=trigger_APP_download_API(platforms,username)
    if result:
        return jsonify(
            {
                "success": True,
                "message": "Triiger API Successfully"
                }
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Triiger API Successfully but restrict"
                }
            )
@python_flask.route('/api/Compensation_api',methods=['POST']) #幸運注單補派獎API
def api_Compensation():
    data=request.get_json(silent=True)
    round_id=data["round_id"]
    isSuccess=Compensation_api.main(round_id)
    
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "Compensation Success"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "Compensation Failed"
                }
            ),500

@python_flask.route('/api/PostCard_api',methods=['POST']) #幸運注單補派獎API
def api_PostCard_Code():
    data=request.get_json(silent=True)
    username=data["username"]
    platforms=data["platforms"] 
    isSuccess=PostCard_Code.main(username,platforms)
    
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "PostCard Bonus receive Success"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "PostCard Bonus receive Failed"
                }
            ),500
        
@python_flask.route('/api/Extra_Reward_api',methods=['POST']) #幸運注單補派獎API
def api_Extra_Reward():
    data=request.get_json(silent=True)
    username=data["username"]
    ticket_id_list=data["ticket_id_list"]
    ticketQuantity=data["amount"]
    promotion_id=data["promotion_id"]
    amount=data["deposit-amount-id"]
    Extra_Promo_ID=data["extra_promo_id"]
    isSuccess=Extra_Reward.main(username, ticket_id_list, ticketQuantity, promotion_id, amount, Extra_Promo_ID)
    
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "Extra Reward receive Success"
                }
            ),200
    else:
        return jsonify(
            {
                "success": False,
                "message": "Extra Reward receive Failed"
                }
            ),500
@python_flask.route('/api/Change_password',methods=['POST']) #變更密碼API
def api_Change_password():
    data=request.json
    username=data["username"]
    platforms=data["platforms"] 
    isSuccess=trigger_change_password_API(username,platforms)
    if isSuccess:
        return jsonify(
            {
                "success": True,
                "message": "Change password Successfully"
                }
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Change password Failed"
                }
            )
        
@python_flask.route('/api/Single_Manual_create',methods=['POST']) #回歸測試 創建個人
def api_manual_create_single():
    
    result = subprocess.run(
    [sys.executable, "-m", "pytest", "test_manual_bonus.py::TestSingleBonus", "-v"],
    cwd="/Users/user/Documents/GitHub/auto_test",
    capture_output=True,
    text=True
    )   
    return {
    "success": result.returncode == 0,
    "summary": result.stdout.split("short test summary info")[-1]
    }
    
@python_flask.route('/api/Single_Manual_create',methods=['POST']) #回歸測試 翻倍獎勵
def api_test_Extra_bonus():
    
    result = subprocess.run(
    [sys.executable, "-m", "pytest", "test_Extra_bonus.py::TestExtraBonus", "-v"],
    cwd="/Users/user/Documents/GitHub/auto_test",
    capture_output=True,
    text=True
    )   
    return {
    "success": result.returncode == 0,
    "summary": result.stdout.split("short test summary info")[-1]
    }
    
@python_flask.route('/api/TICKET_BATCH',methods=['POST']) #前台領取票券API
def api_frontend_receive_ticket():
    data=request.json
    username=data["username"]
    platforms=data["platforms"]  
    frontend_receive_ticket(username,platforms)
    
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
    
@python_flask.route('/api/BONUS_BATCH',methods=['POST']) #前台領取獎勵API
def api_frontend_receive_reward():
    data=request.json
    username=data["username"]
    platforms=data["platforms"]  
    frontend_receive_reward(username,platforms)
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )

@python_flask.route('/api/LOTTERY_BET',methods=['POST']) #前台領取獎勵API
def api_lottery_bet():
    data=request.json
    username=data["username"]
    amount=data["amount"]
    lottery_bet(username,amount)
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
    
@python_flask.route('/api/FRONTEND_DEPOSIT',methods=['POST']) #前台領取獎勵API
def api_Deposit():
    data=request.json
    username=data["username"]
    amount=data["amount"]
    FRONTEND_DEPOSIT.main(username,amount),
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )

@python_flask.route('/api/MANUAL_SIGN',methods=['POST']) #前台領取獎勵API
def api_Manual_Sign():
    data=request.json
    '''
    username=data["username"]
    amount=data["amount"]
    '''
    MANUAL_SIGN.main()
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
@python_flask.route('/api/get_customer_data',methods=['POST']) #查詢玩家資訊API
def api_get_customer_data():
    data=request.json
    username=data["username"]
    platforms=data["platforms"]  
    get_customer_data(username,platforms)
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
@python_flask.route('/api/auto_create_ticket',methods=['POST']) #創建票券API
def api_auto_create_ticket_func():
    data=request.json
    ticket_type=data.get("ticket_type",[]) 
    ticket_input=data.get("ticket_input","")
    platforms=data["platforms"]  
    auto_create_ticket_func(ticket_type,ticket_input,platforms)
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
@python_flask.route('/api/SIGLE_PROMO_7_TICKET',methods=['POST']) #創建7種票券API
def api_auto_create_7_ticket():
    data=request.json
    promotion_id=data["promotion_id"]
    username=data["username"]
    platforms=data["platforms"]  
    manual_create_7_type_tcket(username,promotion_id,platforms)
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
@python_flask.route('/api/MANUAL_CREATE_SINGLE_CONFIRM',methods=['POST']) #手動紅利派發API
def api_manual_create_bonus():
    data=request.json
    promotion_id=data["promotion_id"]
    username=data["username"]
    platforms=data["platforms"]  
    amount=data["amount"]
    promotion_id=data["promotion_id"]
    ticket_id=data["ticket_id"]
    manual_create_bonus(username,platforms,promotion_id,ticket_id,amount)
    if promotion_id:
        return jsonify(
            {
                "success": True,
                "message": "Triiger API Successfully"
                }
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Missing promotion_id"
                }
            )
        
        
@python_flask.route('/api/MANUAL_BATCH',methods=['POST']) #手動紅利派發API
def api_manual_batch():
    data=request.json
    MANUAL_BATCH.main()
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
   
@python_flask.route('/api/DEPOSIT_API',methods=['POST']) #品牌管理員自動審核API
def api_batch_approve_func():
    data=request.json
    platforms=data["platforms"]  
    batch_approve_func(platforms)
    
    return jsonify(
        {
            "success": True,
            "message": "Triiger API Successfully"
            }
        )
@python_flask.route('/api/auto_create_player',methods=['POST']) #創建代理玩家API
def api_auto_create_player():
    data=request.json
    platforms=data["platforms"]  
    username=data["username"]
    result_code, customer_id=auto_create_player(platforms,username)
    if result_code==1:
        success = True,
        message = "Create player and Change password Successfully",
    
    elif result_code==2:
        success = True,
        message = "Create player success but Change password Failed",
        
    elif not result_code:
        success = False,
        message = "Create player Failed"
    return jsonify(
            {
                "success": success,
                "message": message,
                "data":{
                    "customer_id":customer_id
                }
                }
            )
@python_flask.route('/api/create_member_player',methods=['POST']) #新建會員玩家
def  auto_create_member_account():
    
        data=request.json
        username=data["username"]
        amount=data["amount"]
        platforms=data["platforms"] 
        t=threading.Thread(
            target=auto_create_member_player,
            args=(platforms,username,amount),
            daemon=True
        )
        t.start()
        return jsonify(
            {
                "success": True,
                "message": "Async create player & wallet triggered"
            }
        )
    
        
        
@python_flask.route('/api/Customer_id',methods=['POST']) #查看玩家ID API
def api_check_player_detail():
    try:
        data=request.json
        username=data["username"]
        customer_id=Customer_id.main(username)
        if customer_id:
            return jsonify(
                {
                    "success": True,
                    "message": "Triiger API Successfully",
                    "data": {
                        "customer_id":customer_id
                        }
                    }
                )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": "Not receive customer_id",
                    "data": {
                        "customer_id":customer_id
                        }
                    }
                )
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@python_flask.route('/upload_excel', methods=['POST']) 
def upload_excel():
    file=request.files.get('file')
    if not file:
        return jsonify({'message': '沒有選擇檔案'}), 400
    try:
        df=pd.read_excel(file,sheet_name=0)

        full_dupes=df[df.duplicated(keep=False)]
        if  not full_dupes.empty:
            data={
                'message': f"發現 {len(full_dupes)} 筆重複資料",
                'full_dupes':full_dupes.to_dict(orient='records')
            }
            return Response(
                json.dumps(data, ensure_ascii=False,indent=4),
                content_type="application/json; charset=utf-8"
            ), 200
        elif full_dupes.empty:
            data={
                'message': '沒有完全重複的資料'
            }
            return Response(
                json.dumps(data, ensure_ascii=False,indent=4),
                content_type="application/json; charset=utf-8"
            ), 200
        
        elif df['订单号'].nunique()==len(df):
            data={
                'message': '沒有完全重複的資料'
            }
            return Response(
                json.dumps(data, ensure_ascii=False,indent=4),
                content_type="application/json; charset=utf-8"
            ), 200
        else:
            full_dupes=df[df.duplicated(subset=["订单号"], keep=False)]
            data={
                'message': f"發現 {len(full_dupes)} 筆重複資料",
                'data':full_dupes.to_dict(orient='records')
            }
            return Response(
                json.dumps(data, ensure_ascii=False,indent=4),
                content_type="application/json; charset=utf-8"
            ), 200
    except Exception as e:
        print(f"上傳檔案錯誤{e}")
        data={
             'message': f'上傳檔案錯誤: {str(e)}', 'full_dupes': []
        }
        return Response(
                json.dumps(data, ensure_ascii=False,indent=4),
                content_type="application/json; charset=utf-8"
            ), 500
@python_flask.route('/Compare_Two_Excel', methods=['POST']) 
def Compare_Two_Excel():
    key="用户名"
    file_1=request.files.get("file1")
    file_2=request.files.get("file2")
    if not file_1 or not file_2:
         return jsonify({'message': '沒有選擇檔案'}), 400
    set1=set(pd.read_excel(file_1)[key])
    set2=set(pd.read_excel(file_2)[key])

    if set1==set2:
        return jsonify({'message':'excel username一樣'})
    else:
        
        different_file1=sorted(set1-set2)
        different_file2=sorted(set2-set1)
        print("兩個set沒有一樣")
        print(different_file1)
        print(different_file2)
        return jsonify({
             'message':'兩個set沒有一樣',
             'different_file1':different_file1,
             'different_file2':different_file2
                        })



if __name__ == "__main__":
    try:
        python_flask.run(host='0.0.0.0',port=9830,debug=True)
    except Exception as e:
        print(f"啟動錯誤{e}")