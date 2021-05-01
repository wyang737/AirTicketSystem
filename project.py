from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pymysql
from functools import wraps
import ast

app = Flask(__name__)
app.secret_key = "super secret key"
mysql = pymysql.connect(host="localhost", user="root", password="", db="airticketsystem",
						charset="utf8mb4", port=3306, cursorclass=pymysql.cursors.DictCursor, autocommit=True)


def customer_login_required(f):
	@wraps(f)
	def dec(*args, **kwargs):
		if not "username" in session:  # if they're not logged in, make them login
			return redirect(url_for("login"))
		elif session["userType"] != "customer":
			userType = session["userType"]
			if userType == "agent":
				return redirect(url_for("agent"))
			elif userType == "staff":
				return redirect(url_for("staff"))
		return f(*args, **kwargs)

	return dec


def agent_login_required(f):
	@wraps(f)
	def dec(*args, **kwargs):
		if not "username" in session:  # if they're not logged in, make them login
			return redirect(url_for("login"))
		elif session["userType"] != "agent":
			userType = session["userType"]
			if userType == "customer":
				return redirect(url_for("customer"))
			elif userType == "staff":
				return redirect(url_for("staff"))
		return f(*args, **kwargs)

	return dec


def staff_login_required(f):
	@wraps(f)
	def dec(*args, **kwargs):
		if not "username" in session:  # if they're not logged in, make them login
			return redirect(url_for("login"))
		elif session["userType"] != "staff":
			userType = session["userType"]
			if userType == "customer":
				return redirect(url_for("customer"))
			elif userType == "agent":
				return redirect(url_for("agent"))
		return f(*args, **kwargs)

	return dec


# main page
@app.route("/")
def index():
	return render_template("index.html")


# public searching page
@app.route("/publicsearch", methods=["GET", "POST"])
def publicsearch():
	cursor = mysql.cursor()
	query = ""
	info = []
	if request.method == "POST":
		if request.form.get("SearchCity"):
			query = "SELECT airport_name FROM airport WHERE city = \"" + request.form['depCity'] + "\""
			cursor.execute(query)
			dep_airport_names = cursor.fetchall()
			query = "SELECT airport_name FROM airport WHERE city = \"" + request.form['arrCity'] + "\""
			cursor.execute(query)
			arr_airport_names = cursor.fetchall()
			print(arr_airport_names)
			print(dep_airport_names)
			query = "Select * from flight where departure_date = \"" + request.form['depDate'] + "\" and ("
			for dep in dep_airport_names:
				for arr in arr_airport_names:
					query += "(departure_airport = \"" + dep.get(
						'airport_name') + "\" and arrival_airport = \"" + arr.get('airport_name') + "\") or "
			query += "flight_number = -1)"
			#if round trip
			if request.form['retDate']:
				print(query)
		if request.form.get("SearchAirport"):
			query = "SELECT * FROM `flight` WHERE departure_airport = \"" + request.form['depAirport'] + \
					"\" AND arrival_airport = \"" + request.form['arrAirport'] + "\"AND departure_date = \"" + \
					request.form['depDate'] + "\""

		if request.form.get("SearchStatus"):
			query = "SELECT * FROM `flight` WHERE airline_name = \"" + request.form['airlineName'] + \
					"\" AND flight_number = \"" + request.form['flightNumber'] + "\"AND departure_date = \"" + \
					request.form['depDate'] + "\"" + "AND arrival_date = \"" + request.form['arrDate'] + "\""

		return redirect(url_for("results", query=query))
	return render_template("publicsearch.html")


# public searching page
@app.route("/results/<query>", methods=["GET", "POST"])
def results(query):
	cursor = mysql.cursor()
	cursor.execute(query)
	info = cursor.fetchall()
	print(type(info))
	if not "username" in session:
		return render_template("results.html", info=info)
	userType = session["userType"]
	if userType == "customer":
		return render_template("customerresults.html", info=info)
	elif userType == "agent":
		return render_template("agentresults.html", info=info)
	elif userType == "staff":
		return render_template("staffresults.html", info=info)
	return render_template("results.html", info=info)


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
	error = None
	cursor = mysql.cursor()
	if request.method == "POST":
		# check the credentials here...
		customerQuery = "SELECT * FROM customer WHERE customer_email = \"" + request.form[
			'username'] + "\" AND password = \"" + request.form['password'] + "\""
		staffQuery = "SELECT * FROM staff WHERE username = \"" + request.form['username'] + "\" AND password = \"" + \
					 request.form['password'] + "\""
		agentQuery = "SELECT * FROM BookingAgent WHERE booking_agent_email = \"" + request.form[
			'username'] + "\" AND password = \"" + request.form['password'] + "\""
		if cursor.execute(customerQuery):  # successful customer login
			session["username"] = request.form['username']
			session["userType"] = "customer"
			return redirect(url_for('customer'))
		elif cursor.execute(staffQuery):  # successful staff login
			session["username"] = request.form['username']
			session["userType"] = "staff"
			return redirect(url_for('staff'))
		elif cursor.execute(agentQuery):  # successful agent login
			session["username"] = request.form['username']
			session["userType"] = "agent"
			return redirect(url_for('agent'))
		else:  # failed login
			error = "Invalid username/password, please try again."
	return render_template("login.html", error=error)


# logout page
@app.route("/logout", methods=["GET"])
def logout():
	session.pop("username")
	return redirect("/login")


# registration for new users
@app.route("/register", methods=["GET", "POST"])
def register():
	error = None
	if request.method == "POST":
		userType = request.form['userType']  # customer, agent, staff
		if userType == "customer":
			return redirect(url_for('registercustomer'))
		elif userType == "agent":
			return redirect(url_for('registeragent'))
		elif userType == "staff":
			return redirect(url_for('registerstaff'))
	return render_template("register.html", error=error)


# registration for customers
@app.route("/registercustomer", methods=["GET", "POST"])
def registercustomer():
	error = None
	if request.method == "POST":
		cursor = mysql.cursor()
		query = "Select * from customer where customer_email = \"" + request.form['email'] + '\"'
		if cursor.execute(query):  # if the email already exists in the db,
			error = "Email already exists, please try a different email."
			return render_template("registercustomer.html", error=error)
		query = f'''INSERT INTO customer VALUES (\'{request.form['name']}\', \'{request.form['email']}\', 
		\'{request.form['password']}\', {request.form['buildingNumber']}, \'{request.form['street']}\', 
		\'{request.form['city']}\', \'{request.form['state']}\', {request.form['phoneNumber']}, {request.form['passportNumber']},
		\'{request.form['expDate']}\', \'{request.form['passportCountry']}\', \'{request.form['dateOfBirth']}\')'''
		if cursor.execute(query):  # successful registration
			return redirect(url_for('login'))
	return render_template("registercustomer.html", error=error)


# registration for booking agents
@app.route("/registeragent", methods=["GET", "POST"])
def registeragent():
	error = None
	if request.method == "POST":
		cursor = mysql.cursor()
		query = "Select * from BookingAgent where booking_agent_email = \"" + request.form['email'] + '\"'
		if cursor.execute(query):  # if the email already exists in the db,
			error = "Email already exists, please try a different email."
			return render_template("registeragent.html", error=error)
		query = f'''INSERT INTO BookingAgent VALUES (\'{request.form['email']}\', 
		\'{request.form['password']}\', {request.form['agentID']}, 0)'''
		if cursor.execute(query):  # successful registration
			return redirect(url_for('login'))
	return render_template("registeragent.html", error=error)


# registration for airline staff
@app.route("/registerstaff", methods=["GET", "POST"])
def registerstaff():
	error = None
	if request.method == "POST":
		cursor = mysql.cursor()
		query = "Select * from staff where username = \"" + request.form['email'] + '\"'
		if cursor.execute(query):  # if the email already exists in the db,
			error = "Email already exists, please try a different email."
			return render_template("registercustomer.html", error=error)
		# need to parse phone numbers
		numbers = request.form['phoneNumber'].split(", ")
		for num in numbers:
			query = f'''insert into staffphones values (\'{request.form['email']}\', {num})'''
			cursor.execute(query)
		query = f'''INSERT INTO staff VALUES (\'{request.form['email']}\', \'{request.form['password']}\', 
		\'{request.form['name']}\', \'{request.form['dateOfBirth']}\', \'{numbers[0]}\', 
		\'{request.form['airlineName']}\')'''
		if cursor.execute(query):  # successful registration
			return redirect(url_for('login'))
	return render_template("registerstaff.html", error=error)


@app.route("/customer")
@customer_login_required
def customer():
	cursor = mysql.cursor()
	query = "Select name from customer where customer_email = \"" + session['username'] + "\""
	cursor.execute(query)
	name = cursor.fetchone()['name']
	return render_template("customer.html", name=name)


@app.route("/customerflights")
@customer_login_required
def customerflights():
	cursor = mysql.cursor()
	query = "Select ticket_id from purchases where customer_email = \"" + session['username'] + "\""
	cursor.execute(query)
	ticket_ids = cursor.fetchall()
	print(ticket_ids)
	query = "Select flight_number from ticket where ticket_id = "
	for item in ticket_ids:
		query += str(item.get('ticket_id'))
		query += " or ticket_id = "
	query += " -1 "
	print(query)
	cursor.execute(query)
	flight_numbers = cursor.fetchall()
	query = "Select * from flight where (CURRENT_DATE < flight.departure_date OR (CURRENT_DATE = flight.departure_date " \
			"AND CURRENT_TIME < departure_time)) and (flight_number = "
	for item in flight_numbers:
		query += str(item.get('flight_number'))
		query += " or flight_number = "
	query += " -1) "
	cursor.execute(query)
	info = cursor.fetchall()
	# info should be a list of lists, where each inner list is a flight.
	return render_template("customerflights.html", info=info)


@app.route("/customerpurchase", methods=["POST", "GET"])
@customer_login_required
def customerpurchase():
	info = []
	flight_info = ['China Eastern', 'Delayed', 123456789, 'JFK', '2021-03-30', '12:30:12', 'PVG', '2021-03-31',
				   '08:30:59', 500, 1234567890, 0]
	info.append(flight_info)
	flight_info = ['United', 'On Time', 445566778, 'JFK', '2021-03-30', '11:33:22', 'PVG', '2021-03-31', '12:55:11',
				   345, 98989898, 1]
	info.append(flight_info)
	if request.method == "POST":
		form = request.form.to_dict()
		items = list(form.items())[0][0].split(", ")  # so ugly but it works
	return render_template("customerpurchase.html", info=info)


# rating and commenting
@app.route("/rate", methods=["GET", "POST"])
@customer_login_required
def rate():
	error = None
	info = []
	flight_info = ['China Eastern', 'Delayed', 123456789, 'JFK', '2021-03-30', '12:30:12', 'PVG', '2021-03-31',
				   '08:30:59', 500, 1234567890, 0]
	info.append(flight_info)
	flight_info = ['United', 'On Time', 445566778, 'JFK', '2021-03-30', '11:33:22', 'PVG', '2021-03-31', '12:55:11',
				   345, 98989898, 1]
	info.append(flight_info)
	if request.method == "POST":
		form = request.form.to_dict()
		print(form)
		comment = form['comment']
		rating = form['rating']
		flightNumber = list(form)[2]
		customer_email = session['username']

		# first need to check if the customer already rated this flight
		cursor = mysql.cursor()
		query = f'''select customer_email, flight_number from rates where 
		customer_email = \'{customer_email}\' and flight_number = {flightNumber}'''
		if cursor.execute(query):
			error = "You already rated this flight!"
		else:
			query = f'''insert into rates values(\"{customer_email}\", {flightNumber}, \"{comment}\", {rating})'''
			cursor.execute(query)
			error = "Rate & Comment were Succesful!"
			return redirect(url_for('rate'))
	return render_template("rate.html", info=info, error=error)


@app.route("/agent")
@agent_login_required
def agent():
	return render_template("agent.html", name=session['username'])


@app.route("/agentflights")
@agent_login_required
def agentflights():
	cursor = mysql.cursor()
	query = "Select booking_agent_id from bookingagent where booking_agent_email = \"" + session['username'] + "\""
	cursor.execute(query)
	bookingID = cursor.fetchall()
	query = "Select ticket_id from purchases where booking_agent_id = " + str(bookingID[0].get('booking_agent_id'))
	cursor.execute(query)
	ticket_ids = cursor.fetchall()
	print(ticket_ids)
	query = "Select flight_number from ticket where ticket_id = "
	for item in ticket_ids:
		query += str(item.get('ticket_id'))
		query += " or ticket_id = "
	query += " -1 "
	print(query)
	cursor.execute(query)
	flight_numbers = cursor.fetchall()
	query = "Select * from flight where (CURRENT_DATE < flight.departure_date OR (CURRENT_DATE = flight.departure_date " \
			"AND CURRENT_TIME < departure_time)) and (flight_number = "
	for item in flight_numbers:
		query += str(item.get('flight_number'))
		query += " or flight_number = "
	query += " -1) "

	cursor.execute(query)
	info = cursor.fetchall()

	# info should be a list of lists, where each inner list is a flight.
	return render_template("agentflights.html", info=info)


@app.route("/staff")
@staff_login_required
def staff():
	cursor = mysql.cursor()
	query = "Select name from staff where username = \"" + session['username'] + "\""
	cursor.execute(query)
	name = cursor.fetchone()['name']
	return render_template("staff.html", name=name)


@app.route("/staffflights")
@staff_login_required
def staffflights():
	cursor = mysql.cursor()
	query = "Select airline_name from staff where username = \"" + session['username'] + "\""
	cursor.execute(query)
	airline_name = cursor.fetchone().get("airline_name")
	query = "Select * from flight where airline_name = \"" + airline_name + "\""
	cursor.execute(query)
	info = cursor.fetchall()
	customers = []
	query = f"Select flight_number from flight where airline_name = \'{airline_name}\' and CURRENT_DATE < " \
			f"flight.departure_date OR (CURRENT_DATE = flight.departure_date AND CURRENT_TIME < departure_time)"
	cursor.execute(query)
	flightNumbers = cursor.fetchall()
	for num in flightNumbers:
		num = num.get("flight_number")
		query = f'''SELECT customer.name
		from ticket NATURAL JOIN purchases NATURAL JOIN customer
		where ticket.flight_number = {num}'''
		cursor.execute(query)
		names = cursor.fetchall()
		name_list = []
		for name in names:
			name = name.get("name")
			name_list.append(name)
		customers.append(name_list)
	# info should be a list of lists, where each inner list is a flight.
	return render_template("staffflights.html", info=info, customers=customers)


@app.route("/addstuff", methods=["GET", "POST"])
@staff_login_required
def addstuff():
	error = None
	if request.method == "POST":
		cursor = mysql.cursor()
		query = ""
		if len(request.form) == 2:  # it's a new airport
			query = f'''INSERT into airport values (\'{request.form['airportName']}\',
			\'{request.form['city']}\')'''
		elif len(request.form) == 3:  # it's a new airplane
			query = f'''INSERT into airplane values (\'{request.form['airplaneID']}\',
			\'{request.form['numSeats']}\', \'{request.form['airlineName']}\')'''
		else:  # it's a new flight
			status = request.form['status']
			status = "On Time" if status == 'ontime' else 'Delayed'
			query = f'''INSERT into flight values (\'{request.form['airlineName']}\',
			\'{status}\', \'{request.form['flightNumber']}\', \'{request.form['depAirport']}\', 
			\'{request.form['depDate']}\', \'{request.form['depTime']}\', \'{request.form['arrAirport']}\', 
			\'{request.form['arrDate']}\', \'{request.form['arrTime']}\', \'{request.form['basePrice']}\',
			\'{request.form['airplaneID']}\')'''
		cursor.execute(query)
		cursor.close()
	return render_template("addstuff.html", error=error)


@app.route("/changestatus", methods=["GET", "POST"])
@staff_login_required
def changestatus():
	error = None
	if request.method == "POST":
		cursor = mysql.cursor()
		status = request.form['status']
		status = "On Time" if status == 'ontime' else 'Delayed'
		query = f'''update flight set status = \'{status}\' where
		flight_number = \'{request.form['flightNumber']}\' and departure_date = 
		\'{request.form['depDate']}\' and departure_time = \'{request.form['depTime']}\''''
		cursor.execute(query)
		cursor.close()
	return render_template("changestatus.html")


if __name__ == "__main__":
	app.run(host='localhost', port=5000, debug=True)
