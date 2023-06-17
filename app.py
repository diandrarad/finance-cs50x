import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
app.secret_key = 'secret.token_hex(16)'

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Retrieve user's id and cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    # Retrieve user's stocks and their current prices
    stocks = db.execute("SELECT symbol, SUM(shares) AS shares FROM stocks WHERE user_id = ? GROUP BY symbol", session["user_id"])
    cash = cash[0]['cash']

    # Calculate total value of each holding and the overall total value
    total = cash
    for stock in stocks:
        quote = lookup(stock["symbol"])
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["total"] = stock["price"] * stock["shares"]
        total += stock["total"]

        stock['price'] = usd(stock['price'])
        stock['total'] = usd(stock['total'])

    # Render index.html with user's portfolio information
    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Ensure symbol and shares were submitted
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Lookup the stock's current price
        quote = lookup(symbol)
        if quote == None:
            return apology("invalid symbol", 400)
        if not symbol:
            return apology("must provide symbol", 400)
        if not shares:
            return apology("must provide shares", 400)

        # Ensure shares is a positive integer
        try:
            shares = int(shares)
            if shares < 1:
                raise ValueError
        except ValueError:
            return apology("shares must be a positive integer", 400)
        if shares <= 0:
            return apology("shares must be a positive integer", 400)

        # Look up user's cash balance
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if len(cash) != 1:
            return apology("database error", 500)
        cash = cash[0]["cash"]

        # Calculate total cost of purchase
        shares = int(shares)
        total_cost = quote["price"] * shares

        # Ensure user can afford purchase
        if cash < total_cost:
            return apology("can't afford", 403)

        # Add the stock to the stocks table
        db.execute("INSERT INTO stocks (user_id, symbol, shares) VALUES (?, ?, ?)", session["user_id"], quote["symbol"], shares)

        # Add the purchase to the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)",
                   session["user_id"], quote["symbol"], quote["price"], shares)

        # Update the user's cash balance
        db.execute("UPDATE users SET cash = cash - :total_cost WHERE id = :user_id",
                   total_cost=total_cost, user_id=session["user_id"])

        # Redirect user to home page
        flash("Bought!")
        return redirect("/")

    # Render the buy form
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Retrieve all the transactions for the current user from the database
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY transacted DESC", session["user_id"])

    # Render the transactions in an HTML table
    return render_template("history.html", transactions=transactions)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Ensure symbol was submitted
        symbol = lookup(request.form.get("symbol"))
        if not symbol:
            return apology("must provide symbol", 400)

        # Look up the stock quote
        if symbol == None:
            return apology("invalid symbol", 400)

        # Display the stock quote
        return render_template("quoted.html", symbol=symbol)

    # Render the form to get a stock quote
    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password and confirmation was submitted
        elif not password or not request.form.get("confirmation"):
            return apology("must provide password and confirmation", 400)

        if len(password) < 8:
            return apology("Password must be at least 8 characters long")
        if not re.search("[a-z]", password):
            return apology("Password must contain at least one lowercase letter")
        if not re.search("[A-Z]", password):
            return apology("Password must contain at least one uppercase letter")
        if not re.search("[0-9]", password):
            return apology("Password must contain at least one number")

        # Ensure password was submitted
        elif password != request.form.get("confirmation"):
            return apology("passwords must match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("username already exist", 400)

        # Insert new user into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   request.form.get("username"), generate_password_hash(password))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    stocks = db.execute("SELECT symbol FROM stocks WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol or not shares:
            return apology("Please select a stock and number of shares to sell")

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol")

        rows = db.execute("SELECT SUM(shares) AS total_shares FROM stocks WHERE user_id = ? AND symbol = ?", user_id, symbol)
        total_shares = rows[0]["total_shares"]

        try:
            shares = int(shares.strip())
        except ValueError:
            return apology("Shares must be a positive integer")

        if shares > total_shares:
            return apology("you don't have enough shares to sell")

        proceeds = shares * stock["price"]
        print(shares)

        if shares == total_shares:
            db.execute("DELETE FROM stocks WHERE user_id = ? AND symbol = ?", user_id, symbol)
        else:
            db.execute("UPDATE stocks SET shares = shares + ? WHERE user_id = ? AND symbol = ?", -shares, user_id, symbol)

        db.execute("INSERT INTO transactions (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)",
                   user_id, symbol, stock["price"], -shares)

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", proceeds, user_id)

        flash("Sold!")
        return redirect("/")

    return render_template("sell.html", stocks=stocks)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":

        # Get current and new password from form data
        current_password = request.form.get("current_password")
        new_password = request.form.get("password")

        # Ensure password and confirmation was submitted
        if not current_password:
            return apology("must provide current password", 403)

        # Query database for user's current password hash
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Verify current password is correct
        if not check_password_hash(rows[0]["hash"], current_password):
            return apology("Current password is incorrect")

        if len(new_password) < 8:
            return apology("Password must be at least 8 characters long")
        if not re.search("[a-z]", new_password):
            return apology("Password must contain at least one lowercase letter")
        if not re.search("[A-Z]", new_password):
            return apology("Password must contain at least one uppercase letter")
        if not re.search("[0-9]", new_password):
            return apology("Password must contain at least one number")

        if new_password != request.form.get("confirm_password"):
            return apology("passwords must match", 403)

        # Update user's password in database with new hash
        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # If request method is GET, render the change password form
    return render_template("change_password.html")


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    if request.method == "POST":
        # Ensure amount was submitted
        if not request.form.get("amount"):
            return apology("must provide amount", 400)

        # Ensure amount is a positive float
        try:
            amount = float(request.form.get("amount"))
        except ValueError:
            return apology("invalid amount", 400)
        if amount <= 0:
            return apology("amount must be positive", 400)

        # Add the cash to the user's account
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", amount, session["user_id"])

        # Redirect user to index page
        return redirect("/")

    else:
        return render_template("add_cash.html")