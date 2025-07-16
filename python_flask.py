from flask import Flask,render_template,request
import MANUAL_SINGLE,MANUAL_BATCH,PROMOCODE_BATCH,FRONTEND_DEPOSIT,MANUAL_SIGN,NEW_REGISTER_API
from Lott_bet_without_main import implement
from deposit_api import batch_approve
python_flask=Flask(__name__)
@python_flask.route("/")
def hello():
    return render_template("index.html")

@python_flask.route("/submit",methods=['POST'])
def submit():
    selected_scripts=request.form.getlist('script')
    username=request.form.get('username')
    password=request.form.get('password')
    amount=request.form.get('amount')
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
            FRONTEND_DEPOSIT.main(username)
        elif script=='DEPOSIT_API':
            batch_approve()
        elif script=='MANUAL_SIGN':
            MANUAL_SIGN.main()
        elif script=='NEW_REGISTER_API':
            NEW_REGISTER_API.main(username)

    return render_template("index.html",selected_scripts=selected_scripts)
    
if __name__ == "__main__":
    try:
        python_flask.run(debug=True)
    except Exception as e:
        print(f"啟動錯誤{e}")