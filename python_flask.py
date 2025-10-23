from flask import Flask,render_template,request,jsonify,Response,json
import MANUAL_SINGLE,MANUAL_BATCH,PROMOCODE_BATCH,FRONTEND_DEPOSIT,MANUAL_SIGN,NEW_REGISTER_API,Customer_id,auto_create_ticket,Manual_create_single_with_confirm,SameTimeLogin_manager,SIGLE_PROMO_7_TICKET,PLAYER_RANK,Condition_create_bonus,ALL_deposit_promotion,Frontend_receive_reward,Frontend_receive_ticket
from Lott_bet_without_main import implement
from deposit_api import batch_approve
import pandas as pd
python_flask=Flask(__name__)

@python_flask.route("/")
def hello():
    return render_template("index.html")
def auto_create_player(platform_type,username):
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                NEW_REGISTER_API.main(platform,username)

def batch_approve_func(deposit_platform_type):
        for platform in deposit_platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                batch_approve(platform)

def manual_create_bonus(username,promotion,ticket_id,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                Manual_create_single_with_confirm.main(username,promotion,ticket_id,platform)

def manual_create_7_type_tcket(username,promotion,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                SIGLE_PROMO_7_TICKET.main(username,promotion,platform)

def auto_create_ticket_func(ticket_type):
    ticket_input=request.form.get('ticket_input')
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
            auto_create_ticket.main(ticket,localizations)
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
            auto_create_ticket.main(ticket,localizations)

def frontend_receive_reward(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                Frontend_receive_reward.main(username,platform)

def frontend_receive_ticket(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                Frontend_receive_ticket.main(username,platform)

def get_customer_data(username,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','tcgdemov3','rollbet','lodibet'):
                customer_detail=Customer_id.main(username,platform)
                return customer_detail
            return None,None,None
        
@python_flask.route("/submit",methods=['POST'])
def submit():
    try:
        selected_scripts=request.form.getlist('script')
        ticket_type=request.form.getlist('ticket_type')
        username_raw=request.form.get('username',"")
        password=request.form.get('password')
        amount=request.form.get('amount')
        promotion=request.form.get('promotion_id')
        platform_type=request.form.getlist('platform_type_manual')
        ticket_id=request.form.get('ticket_id')
        usernames=[]
        customer_Id = None
        customer_Rank = None
        Deposit_Count = None
        promo=None
        ticket = None
        platform=None
        customer_data = [None, None, None] 
        for u in username_raw.split(","):
            cleaned=u.strip()
            if cleaned:
                usernames.append(cleaned)
                print(usernames)

        
        def get_script_map(username):

            return{
                'MANUAL_SINGLE':lambda:MANUAL_SINGLE.main(),
                'SIGLE_PROMO_7_TICKET':lambda:manual_create_7_type_tcket(username,promotion,platform_type),
                'MANUAL_BATCH':lambda:MANUAL_BATCH.main(),
                "MANUAL_CREATE_SINGLE_CONFIRM":lambda:manual_create_bonus(username,promotion,ticket_id,platform_type),
                'PROMOCODE_BATCH':lambda:PROMOCODE_BATCH.main(username),
                'LOTTERY_BET':lambda:implement(username,password,amount),
                'FRONTEND_DEPOSIT':lambda:FRONTEND_DEPOSIT.main(username,password,amount),
                'DEPOSIT_API':lambda:batch_approve_func(platform_type),
                'MANUAL_SIGN':lambda:MANUAL_SIGN.main(),
                'auto_create_player':lambda:auto_create_player(platform_type,username),
                'Customer_id':lambda:customer_data.__setitem__(slice(0,3),get_customer_data(username,platform_type)),
                'auto_create_ticket':lambda:auto_create_ticket_func(ticket_type),
                'SameTimeLogin':lambda:SameTimeLogin_manager.main(),
                'PLAYER_RANK':lambda:PLAYER_RANK.main(username),
                'Codition_create_bonus':lambda:Condition_create_bonus.main(),
                'BONUS_BATCH':lambda:frontend_receive_reward(username,platform_type),
                'TICKET_BATCH':lambda:frontend_receive_ticket(username,platform_type)

            }
        for script in selected_scripts:
            if script in ['MANUAL_SINGLE', 'MANUAL_BATCH', 'DEPOSIT_API', 'MANUAL_SIGN', 
                            'auto_create_ticket', 'SameTimeLogin', 'Codition_create_bonus']:
                script_map=get_script_map(None)
                action=script_map.get(script)
                if action:
                    action()
                else:
                    print("未知腳本")
            elif script == 'ALL_deposit_promotion':
                ALL_deposit_promotion.main(usernames,password),
            else:
                for username in usernames:
                    script_map=get_script_map(username)
                    action=script_map.get(script)
                    if action:
                        action()
                    else:
                        print("未知腳本")

        return render_template("index.html",
                            selected_scripts=selected_scripts,
                            customer_Id=customer_data[0],
                            customer_rank=customer_data[1],
                            deposit_count=customer_data[2],
                            ticket=ticket,
                            promotion=promotion,
                            platform=platform,
                            ticket_type=ticket_type,
                            )
    except Exception as e:
         return render_template("index.html", error=str(e))

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
    



if __name__ == "__main__":
    try:
        python_flask.run(host='0.0.0.0',port=9830,debug=True)
    except Exception as e:
        print(f"啟動錯誤{e}")