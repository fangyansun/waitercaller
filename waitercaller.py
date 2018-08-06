import datetime
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import current_user
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from forms import RegistrationForm
from forms import LoginForm
from user import User
from passwordhelper import PasswordHelper
from bitlyhelper import BitlyHelper
import config
if config.test:
	from mockdbhelper import MockDBHelper as DBHelper
	route_prefix = ""
else:
	from dbhelper import DBHelper
	route_prefix = "/waitercaller1"



app = Flask(__name__)
app.secret_key = 'tPXJY3X37Qybz4QykV+hOyUabceEXf1Ao2C8upz+fGQXKsM'
login_manager = LoginManager(app)
DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()



@app.route("/")
def home():
	registrationform = RegistrationForm()
	return render_template("home.html", loginform=LoginForm(), registrationform = registrationform)


@app.route("/account")
@login_required
def account():
	tables 		= DB.get_tables(current_user.get_id())
	return render_template("account.html", tables = tables)

@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
	tablename 	= request.form.get("tablenumber")
	tableid 	= DB.add_table(tablename, current_user.get_id())
	new_url		= BH.shorten_url(config.base_url + "newrequest/" + tableid)
	DB.update_table(tableid, new_url)
	return redirect(url_for("account"))


@app.route("/account/deletetable", methods=["POST"])
@login_required
def account_deletetable():
	tableid 	= request.form.get("tableid")
	DB.delete_table(tableid)
	return redirect(url_for("account"))


@app.route("/dashboard")
@login_required
def dashboard():
	now 		= datetime.datetime.now()
	requests 	= DB.get_requests(current_user.get_id())
	for req in requests:
		deltaseconds = (now - req["time"]).seconds
		req["wait_minutes"] ="{}.{}".format((deltaseconds/60), str(deltaseconds%60).zfill(2))
	return render_template("dashboard.html", requests=requests)


@app.route("/dashboard/resolve", methods=["POST"])
@login_required
def dashboard_resolve():
	request_id 	= request.form.get("request_id")
	DB.delete_request(request_id)
	return redirect(url_for("dashboard"))


@app.route("/newrequest/<tid>")
def new_request(tid):
	DB.add_request(tid, datetime.datetime.now())
	return "Your request has been logged and a waiter will be with you shortly"


@app.route("/login", methods=["POST"])
def login():
	form = LoginForm(request.form)
	if form.validate():
		stored_user = DB.get_user(form.loginemail.data)
		if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']):
			user 	= User(form.loginemail.data)
			login_user(user, remember = True)
			return redirect(url_for("account"))
		form.loginemail.errors.append("Email or password invalid")	
	return render_template("home.html", loginform=form, registrationform=RegistrationForm())


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("home"))


@login_manager.user_loader
def load_user(user_id):
	user_password = DB.get_user(user_id)
	if user_password:
		return User(user_id)	


@app.route("/register", methods=["POST"])
def register():
	form = RegistrationForm(request.form)
	if form.validate():
		if DB.get_user(form.email.data):
			form.email.errors.append("Email address already registered")
			return render_template("home.html", loginform=LoginForm(), registrationform = form)
		salt 		= PH.get_salt()
		hashed 		= PH.get_hash(form.password2.data + salt)
		DB.add_user(form.email.data, salt, hashed)
		return render_template("home.html", loginform=LoginForm(), registrationform = form, onloadmessage="RegistrationForm successful. Please log in.")
	return render_template("home.html", loginform=LoginForm(), registrationform = form)


if __name__ == '__main__':
	app.run(port=5000, debug=True)