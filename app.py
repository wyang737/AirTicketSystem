from flask import Flask, render_template, request, session, redirect, url_for, send_file
import pymysql

app = Flask(__name__)

mysql = pymysql.connect(host="localhost", user="root", password="", db="airplane", charset="utf8mb4", port=3306,
                        cursorclass=pymysql.cursors.DictCursor, autocommit=True)


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


# login page
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    cursor = mysql.cursor()
    if request.method == "POST":
        # check the credentials here...
        if not cursor.execute("SELECT * FROM customer WHERE customer_email = " + request.form['username'] +
                          " AND password = " + request.form['password']):
            error = "Invalid username/password, please try again."
        else:
            session["username"] = request.form['username']
            return redirect(url_for("home"))
    return render_template("login.html")


# registration for new users
@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
