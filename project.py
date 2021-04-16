from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# main page
@app.route("/")
def index():
	return render_template("index.html")

# home page
@app.route("/home")
def home():
	return render_template("home.html")

# public searching page
@app.route("/publicsearch")
def publicsearch():
	return render_template("publicsearch.html")

#login page
@app.route("/login", methods=["GET", "POST"])
def login():
	error = None
	if request.method == "POST":
		# check the credentials here...
		if request.form['username'] != 'root' or request.form['password'] != 'password':
			error = 'Invalid username/password, please try again.'
		else:
			return redirect(url_for('index'))
	return render_template("login.html")

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
		# if username & password are in the database, throw some kind of error
		# otherwise, should add them as a tuple into the db
	return render_template("register.html")

@app.route("/customer")
def customer():
	return render_template("customer.html")

@app.route("/agent")
def agent():
	return render_template("agent.html")

@app.route("/staff")
def staff():
	return render_template("staff.html")

@app.route("/addstuff", methods=["GET", "POST"])
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
	return render_template("addstuff.html")


if __name__ == "__main__":
	app.run(host = 'localhost', port = 5000, debug = True)
