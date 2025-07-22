from flask import Flask,render_template,request
import MANUAL_SINGLE,MANUAL_BATCH,PROMOCODE_BATCH,FRONTEND_DEPOSIT,MANUAL_SIGN,NEW_REGISTER_API,Customer_id,auto_create_ticket
from Lott_bet_without_main import implement
from deposit_api import batch_approve
python_flask=Flask(__name__)
@python_flask.route("/")
def hello():
    return render_template("index.html")

@python_flask.route("/submit",methods=['POST'])
def submit():
    selected_scripts=request.form.getlist('script')
    ticket_type=request.form.getlist('ticket_type')
    username=request.form.get('username')
    password=request.form.get('password')
    amount=request.form.get('amount')
    customer_Id = None
    customer_Rank = None
    Deposit_Count = None
    ticket = None
    for script in selected_scripts:
        if script=='MANUAL_SINGLE':
            MANUAL_SINGLE.main()
        elif script=='MANUAL_BATCH':
            MANUAL_BATCH.main()
        elif script=='PROMOCODE_BATCH':
            PROMOCODE_BATCH.main()
        elif script=='LOTTERY_BET':
            implement(username,password,amount)
        elif script=='FRONTEND_DEPOSIT':
            FRONTEND_DEPOSIT.main(username,password,amount)
        elif script=='DEPOSIT_API':
            batch_approve()
        elif script=='MANUAL_SIGN':
            MANUAL_SIGN.main()
        elif script=='NEW_REGISTER_API':
             NEW_REGISTER_API.main(username)
        elif script=="Customer_id":
            customer_Id,customer_Rank,Deposit_Count=Customer_id.main(username)
        elif script=="auto_create_ticket":
            ticket_name_default="default_name"
            for ticket in ticket_type:
                ticket_name=request.form.get('ticket_input')
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
                elif ticket=='CASH' or ticket=='FREE_SPIN' or ticket=='TEMU':
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
                elif ticket=='RAFFLE' or ticket=='GOLDEN_EGG' or ticket=='WHEEL' or ticket=='GIFT' or ticket=='RAFFLE':
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
    return render_template("index.html",selected_scripts=selected_scripts,customer_Id=customer_Id,customer_Rank=customer_Rank,Deposit_Count=Deposit_Count,ticket=ticket)
    
if __name__ == "__main__":
    try:
        python_flask.run(debug=True)
    except Exception as e:
        print(f"啟動錯誤{e}")