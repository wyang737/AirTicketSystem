from flask import Flask, Markup, render_template, request, redirect, url_for, session, send_file
import datetime
import pymysql
from functools import wraps
import ast
import hashlib

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
		cursor.close()
		return redirect(url_for("results", queryDep=queryDep, queryRet=queryRet))
	cursor.close()
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
	cursor.close()
	return render_template("results.html", info=info, info1=info1)

# login page
@app.route("/login", methods=["GET", "POST"])
def login():
	error = None
	cursor = mysql.cursor()
	if request.method == "POST":
		# check the credentials here...
		hex_hashed = hashlib.md5(request.form['password'].encode()).hexdigest()
		customerQuery = "SELECT * FROM customer WHERE customer_email = \"" + request.form[
			'username'] + "\" AND password = \"" + hex_hashed + "\""
		staffQuery = "SELECT * FROM staff WHERE username = \"" + request.form['username'] + "\" AND password = \"" + \
					 hex_hashed + "\""
		agentQuery = "SELECT * FROM BookingAgent WHERE booking_agent_email = \"" + request.form[
			'username'] + "\" AND password = \"" + hex_hashed + "\""
		if cursor.execute(customerQuery):  # successful customer login
			session["username"] = request.form['username']
			session["userType"] = "customer"
			cursor.close()
			return redirect(url_for('customer'))
		elif cursor.execute(staffQuery):  # successful staff login
			session["username"] = request.form['username']
			session["userType"] = "staff"
			query = f'''SELECT airline_name
			from staff
			WHERE username = \'{session["username"]}\''''
			cursor.execute(query)
			airline_name = cursor.fetchone()['airline_name']
			session['airline_name'] = airline_name
			cursor.close()
			return redirect(url_for('staff'))
		elif cursor.execute(agentQuery):  # successful agent login
			session["username"] = request.form['username']
			session["userType"] = "agent"
			idQuery = f'''Select booking_agent_id from bookingagent where 
			booking_agent_email = \'{request.form['username']}\''''
			cursor.execute(idQuery)
			agentID = cursor.fetchone()['booking_agent_id']
			session["agentID"] = str(agentID)
			cursor.close()
			return redirect(url_for('agent'))
		else:  # failed login
			error = "Invalid username/password, please try again."
	cursor.close()
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
		pw2hash = request.form['password']
		hashed = hashlib.md5(pw2hash.encode())
		hex_hashed = hashed.hexdigest()
		query = f'''INSERT INTO customer VALUES (\'{request.form['name']}\', \'{request.form['email']}\', 
		\'{hex_hashed}\', {request.form['buildingNumber']}, \'{request.form['street']}\', 
		\'{request.form['city']}\', \'{request.form['state']}\', {request.form['phoneNumber']}, {request.form['passportNumber']},
		\'{request.form['expDate']}\', \'{request.form['passportCountry']}\', \'{request.form['dateOfBirth']}\')'''
		if cursor.execute(query):  # successful registration
			cursor.close()
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
		pw2hash = request.form['password']
		hashed = hashlib.md5(pw2hash.encode())
		hex_hashed = hashed.hexdigest()
		query = f'''INSERT INTO BookingAgent VALUES (\'{request.form['email']}\', 
		\'{hex_hashed}\', {agentID}, 0)'''
		if cursor.execute(query):  # successful registration
			cursor.close()
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
		pw2hash = request.form['password']
		hashed = hashlib.md5(pw2hash.encode())
		hex_hashed = hashed.hexdigest()
		query = f'''INSERT INTO staff VALUES (\'{request.form['email']}\', \'{hex_hashed}\', 
		\'{request.form['name']}\', \'{request.form['dateOfBirth']}\', \'{numbers[0]}\', 
		\'{request.form['airlineName']}\')'''
		if cursor.execute(query):  # successful registration
			cursor.close()
			return redirect(url_for('login'))
	return render_template("registerstaff.html", error=error)


@app.route("/customer")
@customer_login_required
def customer():
	cursor = mysql.cursor()
	query = "Select name from customer where customer_email = \"" + session['username'] + "\""
	cursor.execute(query)
	name = cursor.fetchone()['name']
	cursor.close()
	return render_template("customer.html", name=name)


@app.route("/customerflights")
@customer_login_required
def customerflights():
	cursor = mysql.cursor()
	query = "Select ticket_id from purchases where customer_email = \"" + session['username'] + "\""
	cursor.execute(query)
	ticket_ids = cursor.fetchall()
	query = "Select flight_number from ticket where ticket_id = "
	for item in ticket_ids:
		query += str(item.get('ticket_id'))
		query += " or ticket_id = "
	query += " -1 "
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
	cursor.close()
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
	now = datetime.datetime.now()
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
		query = f'''insert into purchases values ({ticket_id}, \'{session['username']}\',
		null, {base_price}, {date}, {time}, \'{request.form['cardType']}\', {request.form['cardNumber']},
		\'{request.form['cardName']}\', \'{request.form['expDate']}\')'''
		cursor.execute(query)

		query = f'''insert into ticket values ({ticket_id}, \'{airline_name}\',
		{flight_number})'''
		cursor.execute(query)
		error = "Succesful Purchase!"
	cursor.close()
	return render_template("customerpurchase.html", name=airline_name,\
	 number=flight_number, price=base_price, error=error, date = depDate, time = depTime)


# rating and commenting
@app.route("/rate", methods=["GET", "POST"])
@customer_login_required
def rate():
	cursor = mysql.cursor()
	error = None
	query = f'''SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight
	WHERE customer_email = \'{session['username']}\' AND arrival_date < CURRENT_DATE()'''
	cursor.execute(query)
	info = cursor.fetchall()
	if request.method == "POST":
		form = request.form.to_dict()
		comment = form['comment']
		rating = form['rating']
		flightNumber = list(form)[2]
		customer_email = session['username']
		# first need to check if the customer already rated this flight
		query = f'''select customer_email, flight_number from rates where 
		customer_email = \'{customer_email}\' and flight_number = {flightNumber}'''
		if cursor.execute(query):
			error = "You already rated this flight!"
		else:
			query = f'''insert into rates values(\"{customer_email}\", {flightNumber}, \"{comment}\", {rating})'''
			cursor.execute(query)
			error = "Rate & Comment were Succesful!"
			cursor.close()
	cursor.close()
	return render_template("rate.html", info=info, error=error)

# track my spending
@app.route("/spending", methods=["POST", "GET"])
@customer_login_required
def spending():
	today = datetime.datetime.now()
	# default shows spendings from the past year
	one_year_ago = today - datetime.timedelta(days = 365)
	date2 = today.strftime("%Y-%m-%d")
	date1 = one_year_ago.strftime("%Y-%m-%d")
	cursor = mysql.cursor()
	query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
	and purchase_date > \'{date1}\''''
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
		extra = 6 - current_month
		for x in range((13 - extra), 13): # last year's months
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {x} and year(purchase_date) = {current_year - 1}'''
			cursor.execute(query)
			monthly_spending = 0
			for price in cursor.fetchall():
				monthly_spending += price['sold_price']
			values.append(monthly_spending)
		for x in range(1, current_month + 1): # this year's months
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {x} and year(purchase_date) = {current_year}'''
			cursor.execute(query)
			monthly_spending = 0
			for price in cursor.fetchall():
				monthly_spending += price['sold_price']
			values.append(monthly_spending)

	if request.method == "POST": # recalculate total
		values = []
		date1 = request.form['date1']
		date2 = request.form['date2']
		datetime1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
		datetime2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
		bar_labels = labels
		query = f''' select sold_price from purchases where customer_email = \'{session['username']}\'
		and purchase_date > \'{date1}\' and purchase_date < \'{date2}\''''
		cursor.execute(query)
		total_spending = 0
		for price in cursor.fetchall():
			total_spending += price['sold_price']

		# now get monthly spendings in this new range
		month_diff = 0
		if datetime1.year == datetime2.year:
			bar_labels = labels[datetime1.month - 1:datetime2.month]
			month_diff = datetime2.month - datetime1.month
		else:
			month_diff = (12 - datetime1.month) + datetime2.month
			labels1 = labels[datetime1.month - 1:]
			labels2 = labels[:datetime2.month]
			year_diff = (int(datetime2.strftime("%Y")) - int(datetime1.strftime("%Y")))
			for i in range(1, year_diff):
				month_diff += 12
				labels1 += labels
			bar_labels = labels1 + labels2
		loop_date = datetime2
		for i in range(month_diff + 1):
			month_num = loop_date.strftime("%m")
			year_num = loop_date.strftime("%Y")
			query = f'''select sold_price from purchases where customer_email = \'{session['username']}\'
			and month(purchase_date) = {month_num} and year(purchase_date) = {year_num} and
			purchase_date <= \'{datetime2.strftime("%Y-%m-%d")}\' and purchase_date >= \'{datetime1.strftime("%Y-%m-%d")}\''''
			cursor.execute(query)
			monthly_sum = 0
			for item in cursor.fetchall():
				monthly_sum += item.get("sold_price")
			values.insert(0, monthly_sum)
			loop_date = monthdelta(loop_date, -1)
	cursor.close()
	return render_template("spending.html", total = total_spending, max = 25000, labels=bar_labels, values=values, old=date1, today=date2)

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
	now = datetime.datetime.now()
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
	cursor.close()
	return render_template("agentpurchase.html", name=airline_name,\
	 number=flight_number, price=base_price, error=error, date = depDate, time=depTime)

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
	query = "Select flight_number from ticket where ticket_id = "
	for item in ticket_ids:
		query += str(item.get('ticket_id'))
		query += " or ticket_id = "
	query += " -1 "
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
	cursor.close()
	return render_template("agentflights.html", info=info)

@app.route("/agentcommission", methods=["POST", "GET"])
@agent_login_required
def agentcommission():
    cursor = mysql.cursor()
    bookingID = session['agentID']
    query = "SELECT sum(`sold_price`)/10 from purchases where (purchase_date > ADDDATE(CURRENT_DATE, INTERVAL -30 DAY))" \
            " and booking_agent_id =" + bookingID
    cursor.execute(query)
    commission = cursor.fetchall()[0].get("sum(`sold_price`)/10")
    query = "SELECT COUNT(*) from purchases WHERE (purchase_date > ADDDATE(CURRENT_DATE, INTERVAL -30 DAY))" \
            " and `booking_agent_id` =" + bookingID
    cursor.execute(query)
    tickets = cursor.fetchall()[0].get("COUNT(*)")
    if request.method == "POST":
        query = "SELECT sum(`sold_price`)/10 from purchases where ((purchase_date > \'" + request.form[
            'begDate'] + "\') and (" \
                         "purchase_date < \'" + request.form['endDate']
        query += "\')) and booking_agent_id =" + bookingID
        cursor.execute(query)
        commission = cursor.fetchall()[0].get("sum(`sold_price`)/10")
        query = "SELECT COUNT(*) from purchases WHERE ((purchase_date > \'" + request.form['begDate'] + "\') and (" \
                                                                                                        "purchase_date < \'" + \
                request.form['endDate']
        query += "\')) and booking_agent_id =" + bookingID
        cursor.execute(query)
        tickets = cursor.fetchall()[0].get("COUNT(*)")
        cursor.close()
        return render_template("agentcommissionresults.html", commission=commission, tickets=tickets)
    cursor.close()
    return render_template("agentcommission.html", commission=commission, tickets=tickets)

@app.route("/topcustomers")
@agent_login_required
def topcustomers():
	cursor = mysql.cursor()
	bookingID = session['agentID']
	query = "SELECT `customer_email`, count(*) FROM purchases WHERE purchase_date > ADDDATE(CURRENT_DATE, " \
			"INTERVAL -6 MONTH) and booking_agent_id = " + bookingID + " GROUP BY " \
			"`customer_email` ORDER BY COUNT(*) DESC LIMIT 5 "
	cursor.execute(query)
	toptickets = cursor.fetchall()
	topcusttick = []
	label = []
	query = "SELECT `customer_email`, sum(sold_price)/10 FROM purchases WHERE purchase_date > ADDDATE(CURRENT_DATE, " \
			"INTERVAL -1 YEAR) and booking_agent_id = " + bookingID + " GROUP BY " \
			"`customer_email` ORDER BY sum(sold_price)/10 DESC LIMIT 5"
	cursor.execute(query)
	topcustcomm = []
	label2 = []
	topcommissions = cursor.fetchall()
	for item in toptickets:
		label.append(item["customer_email"])
		topcusttick.append(item["count(*)"])
	for item in topcommissions:
		label2.append(item["customer_email"])
		topcustcomm.append(item['sum(sold_price)/10'])
	cursor.close()
	return render_template("topcustomers.html", labels=label, topcusttick=topcusttick, labels2=label2,
						   topcustcomm=topcustcomm, max=20, max2=500)


@app.route("/staff")
@staff_login_required
def staff():
	cursor = mysql.cursor()
	query = "Select name from staff where username = \"" + session['username'] + "\""
	cursor.execute(query)
	name = cursor.fetchone()['name']
	cursor.close()
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
	customers = []
	query = f"Select flight_number from flight where airline_name = \'{airline_name}\' and ((CURRENT_DATE < " \
			f"flight.departure_date) OR (CURRENT_DATE = flight.departure_date AND CURRENT_TIME < departure_time)) and" \
			f"(flight.departure_date < ADDDATE(CURRENT_DATE, INTERVAL 30 DAY))"
	cursor.execute(query)
	flightNumbers = cursor.fetchall()
	query = "Select * from flight where flight_number = "
	for item in flightNumbers:
		query += str(item.get('flight_number'))
		query += " or flight_number = "
	query += " -1 "
	cursor.execute(query)
	info = cursor.fetchall()
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
	cursor.close()
	return render_template("staffflights.html", info=info, customers=customers)

@app.route("/addstuff", methods=["GET", "POST"])
@staff_login_required
def addstuff():
	error = None
	if request.method == "POST":
		cursor = mysql.cursor()
		query = ""
		if request.form.get("airport"):  # it's a new airport
			query = f'''INSERT into airport values (\'{request.form['airportName']}\',
			\'{request.form['city']}\')'''
		elif request.form.get("airplane"):  # it's a new airplane
			query = f'''INSERT into airplane values (\'{request.form['airplaneID']}\',
			\'{request.form['numSeats']}\', \'{session['airline_name']}\')'''
		else:  # it's a new flight
			status = request.form['status']
			status = "On Time" if status == 'ontime' else 'Delayed'
			query = f'''INSERT into flight values (\'{session['airline_name']}\',
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

@app.route("/frequent")
@staff_login_required
def frequent():
	cursor = mysql.cursor()
	info = []
	flights = []
	dictionary = {}
	flights = []
	# from one year ago - now
	date = datetime.datetime.now() - datetime.timedelta(days = 365)
	query = f'''SELECT customer_email, count(ticket_id)
	FROM purchases NATURAL JOIN ticket
	WHERE airline_name = \'{session['airline_name']}\'
	AND purchase_date >= \'{date.strftime("%Y-%m-%d")}\'
    group by customer_email
	order by count(ticket_id) desc limit 5'''
	cursor.execute(query)
	for elem in cursor.fetchall():
		dictionary[elem.get("customer_email")] = elem.get('count(ticket_id)')
	for customer_email in dictionary.keys():
		query = f'''select * from customer where customer_email = \'{customer_email}\''''
		cursor.execute(query)
		result = cursor.fetchall()
		info.append(result)
	# now get data on flights
	for item in info:
		email = item[0].get('customer_email')
		query = f'''select flight_number 
		from ticket natural join purchases
		where airline_name = \'{session['airline_name']}\'
		and customer_email = \'{email}\''''
		cursor.execute(query)
		flight_list = cursor.fetchall()
		flights.append(flight_list)
	cursor.close()
	return render_template("frequent.html", info=info, flights=flights)

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

@app.route("/reports", methods=["POST", "GET"])
@staff_login_required
def reports():
	values = []
	title = "Number of Tickets Sold"
	total = 0
	# default will show last year?
	date2 = datetime.datetime.now()
	date1 = date2 - datetime.timedelta(days = 365)
	bar_labels = labels[date2.month - 1:] + labels[:date2.month]
	# get monthly number of ticket sales
	cursor = mysql.cursor()
	loop_date = date2
	for i in range(13):
		month_num = loop_date.strftime("%m")
		year_num = loop_date.strftime("%Y")
		loop_date = monthdelta(loop_date, -1)
		query = f'''SELECT count(ticket_id)
		FROM ticket NATURAL JOIN purchases
		WHERE ticket.airline_name = \'{session['airline_name']}\' 
		and extract(month from purchases.purchase_date) = {month_num} 
		AND extract(year from purchases.purchase_date) = {year_num}
		and purchase_date <= \'{date2}\' and purchase_date >= \'{date1}\''''
		cursor.execute(query)
		num_tickets_sold = cursor.fetchone()['count(ticket_id)']
		values.insert(0, num_tickets_sold)
	total = sum(values)
	date1 = date1.strftime("%Y-%m-%d")
	date2 = date2.strftime("%Y-%m-%d")
	if request.method == "POST": # need to recalculate...
		values = []
		date1 = request.form['date1']
		date2 = request.form['date2']
		datetime1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
		datetime2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
		month_diff = 0
		if datetime1.year == datetime2.year:
			bar_labels = labels[datetime1.month - 1:datetime2.month]
			month_diff = datetime2.month - datetime1.month
		else:
			month_diff = (12 - datetime1.month) + datetime2.month
			labels1 = labels[datetime1.month - 1:]
			labels2 = labels[:datetime2.month]
			year_diff = (int(datetime2.strftime("%Y")) - int(datetime1.strftime("%Y")))
			for i in range(1, year_diff):
				month_diff += 12
				labels1 += labels
			bar_labels = labels1 + labels2
		loop_date = datetime2
		for i in range(month_diff + 1):
			month_num = loop_date.strftime("%m")
			year_num = loop_date.strftime("%Y")
			loop_date = monthdelta(loop_date, -1)
			query = f'''SELECT count(ticket_id)
			FROM ticket NATURAL JOIN purchases
			WHERE ticket.airline_name = \'{session['airline_name']}\' 
			and extract(month from purchases.purchase_date) = {month_num} 
			AND extract(year from purchases.purchase_date) = {year_num}
			and purchase_date <= \'{datetime2}\' and purchase_date >= \'{datetime1}\''''
			cursor.execute(query)
			num_tickets_sold = cursor.fetchone()['count(ticket_id)']
			values.insert(0, num_tickets_sold)
		total = sum(values)
	cursor.close()
	return render_template("reports.html", old=date1, today=date2, total=total,values=values, title=title, labels=bar_labels, max=100)

@app.route("/revenue")
@staff_login_required
def revenue():
	title = "View Revenue Comparison"
	pie_labels = ["Direct Sales", "Indirect Sales"]
	colors = ['#0762F5', '#F5AE07']
	# first value is direct sales, second is indirect sales.
	month_values = []
	year_values = []
	airline_name = session['airline_name']
	cursor = mysql.cursor()
	# get previous purchases
	today = datetime.datetime.now()
	one_month_ago = today - datetime.timedelta(days = 30)
	one_year_ago = today - datetime.timedelta(days = 365)
	# last month, direct revenue:
	query = f'''SELECT sum(sold_price)
	FROM ticket NATURAL JOIN purchases
	WHERE ticket.airline_name = \'{airline_name}\' AND 
	purchases.booking_agent_id is null 
	and purchases.purchase_date >= \'{one_month_ago.strftime("%Y-%m-%d")}\''''
	cursor.execute(query)
	month_direct = cursor.fetchone()['sum(sold_price)']
	if (month_direct):
		month_values.append(int(month_direct))
	else:
		month_values.append(0)
	# last month, indirect revenue:
	query = f'''SELECT sum(sold_price)
	FROM ticket NATURAL JOIN purchases
	WHERE ticket.airline_name = \'{airline_name}\'  AND 
	purchases.booking_agent_id is not null 
	and purchases.purchase_date >= \'{one_month_ago.strftime("%Y-%m-%d")}\''''
	cursor.execute(query)
	month_indirect = cursor.fetchone()['sum(sold_price)']
	if (month_indirect):
		month_values.append(int(month_indirect))
	else:
		month_values.append(0)
	# last year, direct revenue:
	query = f'''SELECT sum(sold_price)
	FROM ticket NATURAL JOIN purchases
	WHERE ticket.airline_name = \'{airline_name}\'  AND 
	purchases.booking_agent_id is null 
	and purchases.purchase_date >= \'{one_year_ago.strftime("%Y-%m-%d")}\''''
	cursor.execute(query)
	year_direct = cursor.fetchone()['sum(sold_price)']
	if (year_direct):
		year_values.append(int(year_direct))
	else:
		year_values.append(0)
	# last year, indirect revenue:
	query = f'''SELECT sum(sold_price)
	FROM ticket NATURAL JOIN purchases
	WHERE ticket.airline_name = \'{airline_name}\'  AND 
	purchases.booking_agent_id is not null 
	and purchases.purchase_date >= \'{one_year_ago.strftime("%Y-%m-%d")}\''''
	cursor.execute(query)
	year_indirect = cursor.fetchone()['sum(sold_price)']
	if (year_indirect):
		year_values.append(int(year_indirect))
	else:
		year_values.append(0)
	cursor.close()
	return render_template("revenue.html", title=title, max=25000, m_val = month_values, y_val = year_values, labels = pie_labels, colors = colors)

@app.route("/destinations")
@staff_login_required
def destinations():
	error = None
	today = datetime.datetime.now()
	today_date = today.strftime("%Y-%m-%d")
	month = today.strftime("%m")
	three_months_ago = today - datetime.timedelta(days = 90)
	one_year_ago = today - datetime.timedelta(days = 365)
	
	# get the destinations
	dictionary = {} # city : # of tickets purchased
	months_cities = []
	airports = []
	tickets_purchased = []
	cursor = mysql.cursor()
	query = f'''SELECT DISTINCT airport.city
	FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport
	WHERE flight.arrival_airport = airport.airport_name and 
	flight.airline_name = \'{session['airline_name']}\' and 
	purchase_date >= \'{three_months_ago.strftime("%Y-%m-%d")}\''''
	cursor.execute(query)
	for elem in cursor.fetchall():
		months_cities.append(elem['city'])
	# get the airport names
	for city in months_cities:
		query = f'''select airport_name from airport where city = 
		\'{city}\''''
		cursor.execute(query)
		airport = cursor.fetchone()['airport_name']
		airports.append(airport)
	for i in range(len(months_cities)):
		query = f'''SELECT count(ticket_id)
		FROM ticket NATURAL JOIN flight
		WHERE airline_name = \'{session['airline_name']}\' and 
		arrival_airport = \'{airports[i]}\''''
		cursor.execute(query)
		num_tickets = cursor.fetchone()['count(ticket_id)']
		tickets_purchased.append(num_tickets)
	for i in range(len(months_cities)):
		dictionary[months_cities[i]] = tickets_purchased[i];
	dict(sorted(dictionary.items(), key=lambda item: item[1]))
	months_cities = dictionary.keys()

	# now the past year
	dictionary = {} # city : # of tickets purchased
	airports = []
	tickets_purchased = []
	year_cities = []
	query = f'''SELECT DISTINCT airport.city
	FROM purchases NATURAL JOIN ticket NATURAL JOIN flight, airport
	WHERE flight.arrival_airport = airport.airport_name and 
	flight.airline_name = \'{session['airline_name']}\' and 
	purchase_date >= \'{one_year_ago.strftime("%Y-%m-%d")}\''''
	cursor.execute(query)
	for elem in cursor.fetchall():
		year_cities.append(elem['city'])
	# get the airport names
	for city in year_cities:
		query = f'''select airport_name from airport where city = 
		\'{city}\''''
		cursor.execute(query)
		airport = cursor.fetchone()['airport_name']
		airports.append(airport)
	for i in range(len(year_cities)):
		query = f'''SELECT count(ticket_id)
		FROM ticket NATURAL JOIN flight
		WHERE airline_name = \'{session['airline_name']}\' and 
		arrival_airport = \'{airports[i]}\''''
		cursor.execute(query)
		num_tickets = cursor.fetchone()['count(ticket_id)']
		tickets_purchased.append(num_tickets)
	for i in range(len(year_cities)):
		dictionary[year_cities[i]] = tickets_purchased[i];
	dict(sorted(dictionary.items(), key=lambda item: item[1]))
	year_cities = dictionary.keys()
	cursor.close()
	return render_template("destinations.html", month = months_cities, year = year_cities)

@app.route("/ratings", methods=["POST", "GET"])
@staff_login_required
def ratings():
	cursor = mysql.cursor()
	query = "SELECT * from flight where airline_name = \"" + session["airline_name"] + "\""
	cursor.execute(query)
	info = cursor.fetchall()
	if request.method == "POST":
		flight_number = request.form["flight_number"]
		query = "SELECT AVG(`rating`) FROM `rates` WHERE flight_number =" + flight_number
		cursor.execute(query)
		average = cursor.fetchone()["AVG(`rating`)"]
		if not average:
			average = 0
		query = "SELECT customer_email, comment, rating FROM `rates` WHERE flight_number =" + flight_number
		cursor.execute(query)
		info = cursor.fetchall()
		cursor.close()
		return render_template("ratingresults.html", average=average, info=info)
	cursor.close()
	return render_template("ratings.html", info=info)

@app.route("/topbookingagents")
@staff_login_required
def topbookingagents():
	cursor = mysql.cursor()
	query = "SELECT booking_agent_id, count(*) from purchases natural join ticket " \
			"where booking_agent_id IS NOT NULL and (purchase_date > ADDDATE(CURRENT_DATE, INTERVAL -1 MONTH)) and " \
			"ticket.airline_name = \"" + session["airline_name"] + "\" group by booking_agent_id order by count(*) desc limit 5"
	cursor.execute(query)
	topbytickmonth = cursor.fetchall()
	query = "SELECT booking_agent_id, count(*) from purchases natural join ticket " \
			"where booking_agent_id IS NOT NULL and (purchase_date > ADDDATE(CURRENT_DATE, INTERVAL -1 YEAR)) and " \
			"ticket.airline_name = \"" + session["airline_name"] + "\" group by booking_agent_id order by count(*) desc limit 5"
	cursor.execute(query)
	topbytickyear = cursor.fetchall()
	query = "SELECT booking_agent_id, sum(sold_price)/10 from purchases natural join ticket " \
			"where booking_agent_id IS NOT NULL and (purchase_date > ADDDATE(CURRENT_DATE, INTERVAL -1 YEAR)) and " \
			"ticket.airline_name = \"" + session["airline_name"] + "\" group by booking_agent_id order by sum(sold_price)/10 desc limit 5"
	cursor.execute(query)
	topbycomm = cursor.fetchall()
	cursor.close()
	return render_template("topbookingagents.html", topbytickmonth=topbytickmonth, topbytickyear=topbytickyear, topbycomm=topbycomm)


if __name__ == "__main__":
	app.run(host='localhost', port=5000, debug=True)
