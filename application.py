
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///deals.db")

ISO = [
"AED","ALL","AMD","ANG","AOA","ARS","AUD","AWG","AZN","BAM","BBD","BDT","BGN","BHD",
"BIF","BMD","BND","BOB","BRL","BTN","BWP","BYN","BZD","CAD","CDF","CHF","CLP","CNY",
"COP","CRC","CUC","CUP","CVE","CZK","DJF","DKK","FKP","GBP","GEL","GGP","GHS","GIP",
"GMD","GNF","GTQ","GYD","HKD","HNL","HRK","HTG","HUF","IDR","ILS","IMP","INR","IQD",
"IRR","ISK","JEP","JMD","JOD","JPY","KES","KGS","KHR","KMF","KPW","KRW","KWD","KYD",
"KZT","LAK","LBP","LKR","LRD","LSL","LYD","MAD","MDL","MGA","MKD","MMK","MNT","MOP",
"MRU","MUR","MVR","MWK","MXN","MYR","MZN","NAD","NGN","NIO","NOK","NPR","NZD","OMR",
"PAB","PEN","PGK","PHP","PKR","PLN","PYG","QAR","RON","RSD","RUB","RWF","SAR","SBD",
"SCR","SDG","SEK","SGD","SHP","SLL","SOS","SPL","SRD","STN","SVC","SYP","SZL","THB",
"TJS","TMT","TND","TOP","TRY","TTD","TVD","TWD","TZS","UAH","UGX","USD","UYU","UZS",
"VEF","VND","VUV","WST","XAF","XCD","XDR","XOF","XPF","YER","ZAR","ZMW","ZWD"]

@app.route("/check", methods=["GET", "POST"])
@login_required
def check():

    if request.method == "POST":
        # Ensure national_id was submitted
        if not request.form.get("deal_id"):
            return apology("must provide deal_id", 403)


        deals = db.execute("""SELECT DISTINCT user_id, deal_id, from_iso_code, to_iso_code,
        timestamp, deal_amount FROM deals WHERE deal_id=:deal_id """,
        deal_id=request.form.get("deal_id"))

        dealid=request.form.get("deal_id")
        if len(deals) == 0:
            return render_template("nodeal.html",dealid=dealid)

        return render_template("result.html",deals = deals)

    else:
        return render_template("check.html")

def is_provided(field):
    if not request.form.get(field):
        return apology(f"must provide {field}", 400)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        check_for_errors = is_provided("deal_id") or is_provided("from_iso_code") or is_provided("to_iso_code") or is_provided("deal_amount")

        if check_for_errors:
            return check_for_errors

        deal_id = request.form.get("deal_id")
        from_iso_code = request.form.get("from_iso_code").upper()
        to_iso_code = request.form.get("to_iso_code").upper()
        deal_amount = request.form.get("deal_amount")
        user_id= session["user_id"]

        if from_iso_code not in ISO or to_iso_code not in ISO:
           return apology("invalid ISO code", 403)

        rows = db.execute("""SELECT deal_id FROM deals WHERE deals.deal_id=:deal_id""", deal_id=request.form.get("deal_id"))

        if len(rows) != 0:
           return apology("invalid Deal Id! Deal Id Already Exists", 403)
        db.execute(""" INSERT INTO deals (user_id, deal_id, from_iso_code, to_iso_code, deal_amount)
        VALUES (:user_id, :deal_id, :from_iso_code, :to_iso_code, :deal_amount)""",
                   user_id=session["user_id"],
                   deal_id = request.form.get("deal_id"),
                   from_iso_code=request.form.get("from_iso_code").upper(),
                   to_iso_code=request.form.get("to_iso_code").upper(),
                   deal_amount=request.form.get("deal_amount"))
        flash("Deal Added succesfully!")
        return redirect("/")
    else:
         return render_template("index.html")
    """Buy shares of stock"""


@app.route("/database")
@login_required
def database():
    """Show history of All Deals on the Database"""
    everydeals = db.execute("""SELECT user_id, deal_id, from_iso_code,
        to_iso_code, timestamp, deal_amount FROM deals
    """)

    return render_template("database.html", everydeals=everydeals)

@app.route("/history")
@login_required
def history():
    """Show history of All Deals done by logged in employee"""
    alldeals = db.execute("""SELECT user_id, deal_id, from_iso_code,
        to_iso_code, timestamp, deal_amount FROM deals
        WHERE user_id= :user_id
    """, user_id=session["user_id"])

    return render_template("history.html", alldeals=alldeals)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and both passwords match
        if len(rows) != 0:
            return apology("username already exists", 400)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match, try again", 400)

        prim_key = db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)",
                              username=request.form.get("username"),
                              hash=generate_password_hash(request.form.get("password")))

        if prim_key is None:
            return apology("registration error", 403)
        session["user_id"] = prim_key
        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
