from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pymysql
from functools import wraps

app = Flask(__name__)
app.secret_key = "super secret key"
mysql = pymysql.connect(host="localhost", user="root", password="", db="airticketsystem", 
	charset="utf8mb4", port=3306, cursorclass=pymysql.cursors.DictCursor, autocommit=True)

def login_required(f):
	@wraps(f)
	def dec(*args, **kwargs):
		if not "username" in session:
			return redirect(url_for("login"))
		return f(*args, **kwargs)
	return dec

# main page
@app.route("/")
def index():
	return render_template("index.html")

# public searching page
@app.route("/publicsearch")
def publicsearch():
	return render_template("publicsearch.html")

#login page
@app.route("/login", methods=["GET", "POST"])
def login():
	error = None
	cursor = mysql.cursor()
	if request.method == "POST":
		# check the credentials here...
		query = "SELECT * FROM customer WHERE customer_email = \"" + request.form['username'] + "\" AND password = \"" + request.form['password'] + "\""
		if not cursor.execute(query): # failed login
			error = 'Invalid username/password, please try again.'
		else: 						  # successful login
			session["username"] = request.form['username']
			# probably need to assign session['usertype'] = some query to get the usertype?
			# if usertype = customer, redirect to customer page
			# if staff, redirect to staff...
			# if agent, redirect to agent
			return redirect(url_for('index'))
	return render_template("login.html", error=error)

# registration for new users
@app.route("/register", methods=["GET", "POST"])
def register():
	error = None
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']
		userType = request.form['userType'] # customer, agent, staff
		info = [username, password, userType]
		print (info)
		# if the username already exists in the database,
		# error = "Username already exists"
		# otherwise, should add them as a tuple into the db
	return render_template("register.html", error=error)

@app.route("/customer")
@login_required
def customer():
	return render_template("customer.html", name=session['username'])

@app.route("/agent")
@login_required
def agent():
	return render_template("agent.html")

@app.route("/staff")
@login_required
def staff():
	return render_template("staff.html")

@app.route("/addstuff", methods=["GET", "POST"])
@login_required
def addstuff():
	error = None
	if request.method == "POST":
		info = []
		if len(request.form) == 2:   # it's a new airport
			name = request.form['airportName']
			city = request.form['city']
			# need to add to db now..
		elif len(request.form) == 3: # it's a new airplane
			airplaneID = request.form['airplaneID']
			numSeats = request.form['numSeats']
			name = request.form['airlineName']

			# need to add to db now..
		else:  						 # it's a new flight
			airlineName = request.form['airlineName']
			status = request.form['status'] # ontime or delayed
			flightNumber = request.form['flightNumber']
			depAirport = request.form['depAirport']
			depDate = request.form['depDate'] # of the format 2021-04-22
			depTime = request.form['depTime'] # of the format 00:00 - 23:59 
			arrAirport = request.form['arrAirport']
			arrDate = request.form['arrDate']
			arrTime = request.form['arrTime']
			price = request.form['basePrice']
			airplaneID = request.form['airplaneID']
			# need to add to db now..
	print (request.form)
	return render_template("addstuff.html", error=error)

@app.route("/changestatus", methods=["GET", "POST"])
@login_required
def changestatus():
	error = None
	if request.method == "POST":
		flightNumber = request.form['flightNumber']
		depDate = request.form['depDate'] # of the format 2021-04-22
		depTime = request.form['depTime'] # of the format 00:00 - 23:59 
		newStatus = request.form['status'] # ontime or delayed
		# change the db now...
	return render_template("changestatus.html")


if __name__ == "__main__":
	app.run(host = 'localhost', port = 5000, debug = True)
