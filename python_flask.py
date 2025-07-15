from flask import Flask,render_template,request
python_flask=Flask(__name__)
@python_flask.route("/")
def hello():
    return render_template("index.html")

@python_flask.route("/submit",methods=['POST'])
def submit():
    selected_scripts=request.form.getlist('script')
    return render_template("index.html",selected_scripts=selected_scripts)
    
if __name__ == "__main__":
    python_flask.run(debug=True)