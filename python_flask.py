from flask import Flask,render_template,request
import MANUAL_SINGLE,MANUAL_BATCH,PROMOCODE_BATCH,FRONTEND_DEPOSIT,MANUAL_SIGN,NEW_REGISTER_API,Customer_id,auto_create_ticket,Manual_create_single_with_confirm,SameTimeLogin_manager,SIGLE_PROMO_7_TICKET,PLAYER_RANK
from Lott_bet_without_main import implement
from deposit_api import batch_approve
python_flask=Flask(__name__)
@python_flask.route("/")
def hello():
    return render_template("index.html")
def auto_create_player(platform_type,username):
        for platform in platform_type:
            if platform in ('gi8viet','huamei','TCGDEMOV3','rollbet','lodibet'):
                NEW_REGISTER_API.main(platform,username)

def batch_approve_func(deposit_platform_type):
        for platform in deposit_platform_type:
            if platform in ('gi8viet','huamei','TCGDEMOV3','rollbet','lodibet'):
                batch_approve(platform)

def manual_create_bonus(username,promotion,ticket_id,platform_type):
        print(platform_type)
        for platform in platform_type:
            if platform in ('gi8viet','huamei','TCGDEMOV3','rollbet','lodibet'):
                Manual_create_single_with_confirm.main(username,promotion,ticket_id,platform_type)

def auto_create_ticket_func(ticket_type):
    ticket_name_default="default_name_ALL"
    ticket_input=request.form.get('ticket_input')
    for ticket in ticket_type:
            if ticket=='ALL':
                localizations = [
                    {
                            "language": "CN",
                            "name": ticket_name_default,
                            "description": None,
                            "lossMessage": None,
                            "imageUrl": None,
                            "imageName": None
                        }
                    ]
                auto_create_ticket.main(ticket,localizations)
            elif ticket in ['CASH','FREE_SPIN','TEMU']:

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
@python_flask.route("/submit",methods=['POST'])
def submit():
    
    selected_scripts=request.form.getlist('script')
    ticket_type=request.form.getlist('ticket_type')
    username=request.form.get('username')
    password=request.form.get('password')
    amount=request.form.get('amount')
    promotion=request.form.get('promotion_id')
    platform_type=request.form.getlist('platform_type')
    deposit_platform_type=request.form.getlist('deposit_platform_type')
    platform_type_manual=request.form.getlist('platform_type_manual')
    ticket_id=request.form.get('ticket_id')
    customer_Id = None
    customer_Rank = None
    Deposit_Count = None
    promo=None
    ticket = None
    platform=None
    customer_data = [None, None, None] 
    script_map={
        'MANUAL_SINGLE':lambda:MANUAL_SINGLE.main(),
        'SIGLE_PROMO_7_TICKET':lambda:SIGLE_PROMO_7_TICKET.main(username,promotion),
        'MANUAL_BATCH':lambda:MANUAL_BATCH.main(),
        "MANUAL_CREATE_SINGLE_NOT_CONFIRM":lambda:manual_create_bonus(username,promotion,ticket_id,platform_type_manual),
        'PROMOCODE_BATCH':lambda:PROMOCODE_BATCH.main(username),
        'LOTTERY_BET':lambda:implement(username,password,amount),
        'FRONTEND_DEPOSIT':lambda:FRONTEND_DEPOSIT.main(username,password,amount),
        'DEPOSIT_API':lambda:batch_approve_func(deposit_platform_type),
        'MANUAL_SIGN':lambda:MANUAL_SIGN.main(),
        'auto_create_player':lambda:auto_create_player(platform_type,username),
        "Customer_id":lambda:customer_data.__setitem__(slice(0,3),Customer_id.main(username)),
        "auto_create_ticket":lambda:auto_create_ticket_func(ticket_type),
        "SameTimeLogin":lambda:SameTimeLogin_manager.main(),
        "PLAYER_RANK":lambda:PLAYER_RANK.main(username)

    }
    for script in selected_scripts:
        action=script_map.get(script)
        if action:
            action()
        else:
            print("未知腳本")


    return render_template("index.html",
                           selected_scripts=selected_scripts,
                           customer_Id=customer_data[0],
                           customer_Rank=customer_data[1],
                           Deposit_Count=customer_data[2],
                           ticket=ticket,
                           promotion=promotion,
                           platform=platform,
                           ticket_type=ticket_type,
                           )
    
if __name__ == "__main__":
    try:
        python_flask.run(host='0.0.0.0',port=5000,debug=True)
    except Exception as e:
        print(f"啟動錯誤{e}")