from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import pymysql
from functools import wraps
import ast

app = Flask(__name__)
app.secret_key = "super secret key"
mysql = pymysql.connect(host="localhost", user="root", password="", db="airticketsystem",
						charset="utf8mb4", port=3306, cursorclass=pymysql.cursors.DictCursor, autocommit=True)
labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

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
	queryDep = ""
	queryRet = "Select * from flight where flight_number = -1"
	info = []
	if request.method == "POST":
		if request.form.get("SearchCity"):
			queryDep = "SELECT airport_name FROM airport WHERE city = \"" + request.form['depCity'] + "\""
			cursor.execute(queryDep)
			dep_airport_names = cursor.fetchall()
			queryDep = "SELECT airport_name FROM airport WHERE city = \"" + request.form['arrCity'] + "\""
			cursor.execute(queryDep)
			arr_airport_names = cursor.fetchall()
			cursor.close()
			queryDep = "Select * from flight where departure_date = \"" + request.form['depDate'] + "\" and ("
			for dep in dep_airport_names:
				for arr in arr_airport_names:
					queryDep += "(departure_airport = \"" + dep.get(
						'airport_name') + "\" and arrival_airport = \"" + arr.get('airport_name') + "\") or "
			queryDep += "flight_number = -1)"
			# if round trip
			if request.form['retDate']:
				queryRet = "Select * from flight where arrival_date = \"" + request.form['retDate'] + "\" and ("
				for dep in dep_airport_names:
					for arr in arr_airport_names:
						queryRet += "(departure_airport = \"" + arr.get(
							'airport_name') + "\" and arrival_airport = \"" + dep.get('airport_name') + "\") or "
				queryRet += "flight_number = -1)"
		if request.form.get("SearchAirport"):
			queryDep = "SELECT * FROM `flight` WHERE departure_airport = \"" + request.form['depAirport'] + \
					   "\" AND arrival_airport = \"" + request.form['arrAirport'] + "\"AND departure_date = \"" + \
					   request.form['depDate'] + "\""
			# if round trip
			if request.form['retDate']:
				queryRet = "SELECT * FROM `flight` WHERE departure_airport = \"" + request.form['arrAirport'] + \
						   "\" AND arrival_airport = \"" + request.form['depAirport'] + "\"AND arrival_date = \"" + \
						   request.form['retDate'] + "\""
		if request.form.get("SearchStatus"):
			queryDep = "SELECT * FROM `flight` WHERE airline_name = \"" + request.form['airlineName'] + \
					   "\" AND flight_number = \"" + request.form['flightNumber'] + "\"AND departure_date = \"" + \
					   request.form['depDate'] + "\"" + "AND arrival_date = \"" + request.form['arrDate'] + "\""
		return redirect(url_for("results", queryDep=queryDep, queryRet=queryRet))
	if not "username" in session:
		return render_template("publicsearch.html")
	elif session['userType'] == "customer":
		return render_template("customerps.html")
	elif session['userType'] == "staff":
		return render_template("staffps.html")
	else:
		return render_template("agentps.html")


# public searching page
@app.route("/results/<queryDep>/<queryRet>", methods=["GET", "POST"])
def results(queryDep, queryRet=""):
	cursor = mysql.cursor()
	cursor.execute(queryDep)
	info = cursor.fetchall()
	cursor = mysql.cursor()
	cursor.execute(queryRet)
	info1 = cursor.fetchall()
	if not "username" in session:
		return render_template("results.html", info=info, info1=info1)
	userType = session["userType"]
	if userType == "customer":
		if request.method == "POST":
			flight_info = list(request.form)[0]
			return (redirect(url_for("customerpurchase", flight_info=flight_info)))
		return render_template("customerresults.html", info=info, info1=info1)
	elif userType == "agent":
		if request.method == "POST":
			flight_info = list(request.form)[0]
			return (redirect(url_for("agentpurchase", flight_info=flight_info)))
		return render_template("agentresults.html", info=info, info1=info1)
	elif userType == "staff":
		return render_template("staffresults.html", info=info, info1=info1)
	return render_template("results.html", info=info, info1=info1)


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
			idQuery = f'''Select booking_agent_id from bookingagent where 
			booking_agent_email = \'{request.form['username']}\''''
			cursor.execute(idQuery)
			agentID = cursor.fetchone()['booking_agent_id']
			session["agentID"] = str(agentID)
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
		query = f'''SELECT booking_agent_id 
		FROM bookingagent
		ORDER BY booking_agent_id DESC
		LIMIT 1'''
		cursor.execute(query)
		agentID = cursor.fetchone()['booking_agent_id']
		agentID += 1
		if agentID > 99999:
			agentID = 0
		query = f'''INSERT INTO BookingAgent VALUES (\'{request.form['email']}\', 
		\'{request.form['password']}\', {agentID}, 0)'''
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


@app.route("/customerpurchase/<flight_info>", methods=["POST", "GET"])
@customer_login_required
def customerpurchase(flight_info):
	cursor = mysql.cursor()
	error = None
	info = flight_info.split("|")
	flight_number = info[0]
	airline_name = info[1]
	base_price = info[2]
	depDate = info[3]
	depTime = info[4]

	query = f'''select airplane_id from flight where flight_number = {flight_number}
	and departure_date = \'{depDate}\' and departure_time = \'{depTime}\''''
	cursor.execute(query)
	airplane_id = cursor.fetchone()['airplane_id']
	query = f'''select num_seats from airplane where airplane_id = {airplane_id}'''
	cursor.execute(query)
	num_seats = cursor.fetchone()['num_seats']

	query = f'''select count(*) from ticket where flight_number = {flight_number}'''
	cursor.execute(query)
	num_passengers = cursor.fetchone()['count(*)']
	if num_passengers >= (num_seats * 0.7):
		base_price *= 1.2
	now = datetime.now()
	date = now.strftime("\'%Y-%m-%d\'") # with quotes already!
	time = now.strftime("\'%H:%M:00\'") # with quotes already!

	query = f'''SELECT ticket_id 
	FROM ticket
	ORDER BY ticket_id DESC
	LIMIT 1'''
	cursor.execute(query)
	ticket_id = cursor.fetchone()['ticket_id'] # get the last ticket_id, add 1
	ticket_id += 1
	if ticket_id > 99999999:
		ticket_id = 0 # wrap back around
	if request.method == "POST":
		query = f'''insert into purchases values ({ticket_id}, \'{request.form['email']}\',
		null, {base_price}, {date}, {time}, \'{request.form['cardType']}\', {request.form['cardNumber']},
		\'{request.form['cardName']}\', \'{request.form['expDate']}\')'''
		cursor.execute(query)

		query = f'''insert into ticket values ({ticket_id}, \'{airline_name}\',
		{flight_number})'''
		cursor.execute(query)
		error = "Succesful Purchase!"
	return render_template("customerpurchase.html", name=airline_name,\
	 number=flight_number, price=base_price, error=error, date = depDate, time = depTime)


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

# track my spending
@app.route("/spending", methods=["POST", "GET"])
@customer_login_required
def spending():
	today = datetime.datetime.now()
	# default shows spendings from the past year
	old_datetime = today - datetime.timedelta(weeks = 52)
	today_date = today.strftime("%Y-%m-%d")
	old_date = old_datetime.strftime("%Y-%m-%d")
	cursor = mysql.cursor()
	query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
	and purchase_date > \'{old_date}\''''
	cursor.execute(query)
	total_spending = 0
	for price in cursor.fetchall():
		total_spending += price['sold_price']

	bar_labels = labels
	# getting spendings by month for past 6 months
	values = []
	current_month = int(today.strftime("%m"))
	current_year = int(today.strftime("%Y"))
	if current_month >= 6:
		bar_labels = bar_labels[current_month - 6 : current_month]
		for x in range(1, current_month + 1):
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {x} and year(purchase_date) = {current_year}'''
			cursor.execute(query)
			monthly_spending = 0
			for price in cursor.fetchall():
				monthly_spending += price['sold_price']
			values.append(monthly_spending)

	else: # have to deal with wrapping around of months...
		extras = bar_labels[12 - (6 - current_month):] # get end of last year
		bar_labels = extras + bar_labels[:current_month]
		for x in range(1, current_month + 1): # this year's months
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {x} and year(purchase_date) = {current_year}'''
			cursor.execute(query)
			monthly_spending = 0
			for price in cursor.fetchall():
				monthly_spending += price['sold_price']
			values.append(monthly_spending)
		extra = 6 - current_month
		for x in range((13 - extra), 13): # last year's months
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {x} and year(purchase_date) = {current_year - 1}'''
			cursor.execute(query)
			monthly_spending = 0
			for price in cursor.fetchall():
				monthly_spending += price['sold_price']
			values.append(monthly_spending)

	if request.method == "POST": # recalculate total
		values = []
		old_date = request.form['date1']
		today_date = request.form['date2']
		date1 = old_date
		date2 = today_date
		bar_labels = labels
		query = f''' select sold_price from purchases where customer_email = \'{session['username']}\'
		and purchase_date > \'{date1}\' and purchase_date < \'{date2}\''''
		cursor.execute(query)
		total_spending = 0
		for price in cursor.fetchall():
			total_spending += price['sold_price']

		# now get monthly spendings in this new range
		date1 = date1.split("-")
		year1, month1, day1 = date1
		date2 = date2.split("-")
		year2, month2, day2 = date2
		if int(month1) < int(month2) and year1 == year2: # easy case
			for x in range(int(month1), int(month2) + 1):
				query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
				and month(purchase_date) = {x} and year(purchase_date) = {year1}'''
				cursor.execute(query)
				monthly_spending = 0
				for price in cursor.fetchall():
					monthly_spending += price['sold_price']
				values.append(monthly_spending)
			bar_labels = bar_labels[int(month1) - 1:int(month2)]
		elif int(month1) == int(month2) and year1 == year2: # still easy case
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {month1} and year(purchase_date) = {year1}'''
			cursor.execute(query)
			monthly_spending = 0
			for price in cursor.fetchall():
				monthly_spending += price['sold_price']
			values.append(monthly_spending)
			bar_labels = [bar_labels[int(month1) - 1]] # just one month
		elif int(month1) > int(month2) and int(year1) == int(year2) - 1: # slightly harder case
			for x in range(int(month1), 13): # payments from last year
				query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
				and month(purchase_date) = {x} and year(purchase_date) = {year1}'''
				cursor.execute(query)
				monthly_spending = 0
				for price in cursor.fetchall():
					monthly_spending += price['sold_price']
				values.append(monthly_spending)
			for x in range(1, int(month2) + 1): # payments from this year
				query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
				and month(purchase_date) = {x} and year(purchase_date) = {year2}'''
				cursor.execute(query)
				monthly_spending = 0
				for price in cursor.fetchall():
					monthly_spending += price['sold_price']
				values.append(monthly_spending)
			bar_labels = bar_labels[int(month1) - 1:] + bar_labels[:int(month2)]
	return render_template("spending.html", total = total_spending, max = 10000, labels=bar_labels, values=values, old=old_date, today=today_date)


@app.route("/agent")
@agent_login_required
def agent():
	return render_template("agent.html", name=session['username'])

@app.route("/agent/<flight_info>", methods = ["POST", "GET"])
@agent_login_required
def agentpurchase(flight_info):
	cursor = mysql.cursor()
	error = None
	info = flight_info.split("|")
	flight_number = info[0]
	airline_name = info[1]
	base_price = info[2]
	depDate = info[3]
	depTime = info[4]

	query = f'''select airplane_id from flight where flight_number = {flight_number}
	and departure_date = \'{depDate}\' and departure_time = \'{depTime}\''''
	cursor.execute(query)
	airplane_id = cursor.fetchone()['airplane_id']
	query = f'''select num_seats from airplane where airplane_id = {airplane_id}'''
	cursor.execute(query)
	num_seats = cursor.fetchone()['num_seats']

	query = f'''select count(*) from ticket where flight_number = {flight_number}'''
	cursor.execute(query)
	num_passengers = cursor.fetchone()['count(*)']

	if num_passengers >= (num_seats * 0.7):
		base_price *= 1.2
	now = datetime.now()
	date = now.strftime("\'%Y-%m-%d\'") # with quotes already!
	time = now.strftime("\'%H:%M:00\'") # with quotes already!
	cursor = mysql.cursor()
	query = f'''SELECT ticket_id 
	FROM ticket
	ORDER BY ticket_id DESC
	LIMIT 1'''
	cursor.execute(query)
	ticket_id = cursor.fetchone()['ticket_id'] # get the last ticket_id, add 1
	ticket_id += 1
	if ticket_id > 99999999:
		ticket_id = 0 # wrap back around
	if request.method == "POST":
		query = f'''insert into purchases values ({ticket_id}, \'{request.form['email']}\',
		{session['agentID']}, {base_price}, {date}, {time}, \'{request.form['cardType']}\', {request.form['cardNumber']},
		\'{request.form['cardName']}\', \'{request.form['expDate']}\')'''
		cursor.execute(query)

		# update commission
		query = f'''select commission from bookingagent where booking_agent_id =
		{session['agentID']}'''
		cursor.execute(query)
		commission = cursor.fetchone()['commission']
		commission += int(int(base_price) * 0.1)
		query = f'''update bookingagent set commission = {commission} where 
		booking_agent_email = \'{session['username']}\''''
		cursor.execute(query)

		query = f'''insert into ticket values ({ticket_id}, \'{airline_name}\',
		{flight_number})'''
		cursor.execute(query)
		error = "Succesful Purchase!"
	return render_template("agentpurchase.html", name=airline_name,\
	 number=flight_number, price=base_price, error=error)

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
