import os
import pytz

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime
from flask_mail import Mail, Message

# Configure application
app = Flask(__name__)

# Configure mail bot
app.config["MAIL_DEFAULT_SENDER"] = "hbuddy.cs50@gmail.com"
app.config["MAIL_PASSWORD"] = "38R0berts"
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "hbuddy.cs50@gmail.com"

mail = Mail(app)

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
db = SQL("sqlite:///buddy.db")

# Homepage with welcome carousel


@app.route("/")
def welcome():
    return render_template("welcome.html")


# Dashboard with matches, buttons to update profile and such
@app.route("/dashboard")
def dashboard():
    # Select your name for dashboard
    meinfo = db.execute("SELECT first_name, last_name, class FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]

    # Select all your matches, send this information to the html page to make into cards
    matches1 = db.execute(
        "SELECT id_matcher FROM matches WHERE id_matchee = :user AND matchstatusmatchee = 1 AND matchstatusmatcher = 1", user=session["user_id"])
    matches2 = db.execute(
        "SELECT id_matchee FROM matches WHERE id_matcher = :user AND matchstatusmatchee = 1 AND matchstatusmatcher = 1", user=session["user_id"])

    # You could be the matcher or the matchee
    totalmatches = []
    for i in matches1:
        totalmatches.append(i["id_matcher"])

    for i in matches2:
        totalmatches.append(i["id_matchee"])

    cardinfo = []

    # Selects all information from your matches for the cards on the dashboard
    if len(totalmatches) != 0:
        for i in totalmatches:
            info = db.execute("SELECT * FROM users WHERE user_id = :other_id", other_id=i)
            info[0]["time"] = db.execute("SELECT matchtime,class FROM matches WHERE (id_matcher = :match AND id_matchee=:user_id) \
            OR (id_matchee = :match AND id_matcher=:user_id)", match=i, user_id=session["user_id"])
            info[0]["class"] = db.execute("SELECT class FROM matches WHERE (id_matcher = :match AND id_matchee=:user_id) \
            OR (id_matchee = :match AND id_matcher=:user_id)", match=i, user_id=session["user_id"])

            cardinfo += info

        return render_template("dashboard.html", meinfo=meinfo, cardinfo=cardinfo)

    # If you have no buddies, nothing shows up and a message appears
    return render_template("dashboard.html", meinfo=meinfo)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        if len(rows) != 1:
            return render_template("apology.html", message="Your email does not exist in the H-Buddy database", route="/login")

        # Ensure email exists and password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="Your password was incorrect", route="/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # mm/dd/YY H:M:S
        dt_string = datetime.now().strftime("%m/%d/%Y %H:%M")
        db.execute("UPDATE users SET lastactive = :date WHERE user_id = :user", date=dt_string, user=session["user_id"])

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Triggered when you click "check" next to a match, also performs a check for match (double meaning ...)
@app.route("/check")
def check():
    other_is_matchee = False
    newmatch = False

    # Need to figure out if you are denoted as the matchee or the matcher
    me = db.execute("SELECT id_matchee FROM matches WHERE id_matcher = :user AND currentcard=1",
                    user=session["user_id"])
    orme = db.execute("SELECT id_matcher FROM matches WHERE id_matchee = :user AND currentcard=1",
                      user=session["user_id"])

    if len(me) > 0:
        other_is_matchee = True

    # Different update occurs depending on which you are
    if other_is_matchee:
        db.execute("UPDATE matches SET matchstatusmatcher = 1 WHERE id_matcher = :user AND currentcard = 1",
                   user=session["user_id"])
    else:
        db.execute("UPDATE matches SET matchstatusmatchee = 1 WHERE id_matchee = :user AND currentcard = 1",
                   user=session["user_id"])

    # Checks if a new match was just made
    checknew = db.execute("SELECT id_matcher FROM matches WHERE matchstatusmatcher=1 AND matchstatusmatchee=1 AND currentcard=1")

    if len(checknew) > 0:
        newmatch = True

    # If so, update the match with the time of match and class
    if newmatch:
        dt_string = datetime.now().strftime("%m/%d/%Y %H:%M")

        db.execute("UPDATE matches SET matchtime=:time WHERE currentcard=1", time=dt_string)

        firstinfo = db.execute("SELECT first_name,last_name,email,phone,class FROM users WHERE user_id IN \
        (SELECT id_matchee FROM matches WHERE matchstatusmatcher=1 AND matchstatusmatchee=1 AND currentcard=1)")[0]

        otherinfo = db.execute("SELECT first_name,last_name,email,phone,class FROM users WHERE user_id IN \
        (SELECT id_matcher FROM matches WHERE matchstatusmatcher=1 AND matchstatusmatchee=1 AND currentcard=1)")[0]

        # Send the email!
        msg = Message("New H-Buddy!", recipients=[firstinfo["email"], otherinfo["email"]])
        msg.body = "Congrats! Both of you expressed interest in being each other's pset buddies in " + \
            firstinfo["class"] + ". We've made the introduction, it's your turn to start psetting! \n "
        msg.body += "\n" + firstinfo["first_name"] + " " + firstinfo["last_name"] + \
            " can be reached at " + firstinfo["email"] + " and " + firstinfo["phone"]
        msg.body += "\n" + otherinfo["first_name"] + " " + otherinfo["last_name"] + \
            " can be reached at " + otherinfo["email"] + " and " + otherinfo["phone"]
        mail.send(msg)

    # Different update based on which is matcher/matchee
    if other_is_matchee:
        db.execute("UPDATE matches SET matchstatusmatcher = 1,currentcard=0 WHERE id_matcher = :user AND currentcard = 1",
                   user=session["user_id"])
    else:
        db.execute("UPDATE matches SET matchstatusmatchee = 1,currentcard=0 WHERE id_matchee = :user AND currentcard = 1",
                   user=session["user_id"])

    # Redirect to generate a new buddy card
    return redirect("/buddyfinder")


# If you press x on the match, it is a simple update to -1
@app.route("/ex")
def ex():
    db.execute("UPDATE matches SET matchstatusmatcher = -1, currentcard = 0 WHERE id_matcher = :user AND currentcard = 1",
               user=session["user_id"])
    db.execute("UPDATE matches SET matchstatusmatchee = -1, currentcard = 0 WHERE id_matchee = :user AND currentcard = 1",
               user=session["user_id"])

    return redirect("/buddyfinder")


# Register a user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("apology.html", message="Your passwords did not match", route="/register")

        email = request.form.get("email")

        # Confirm this is a Harvard email
        if email.split("@")[1] != "college.harvard.edu":
            return render_template("apology.html", message="Please use your Harvard email to sign up", route="/register")

        # Check if someone is already in the database
        rows = db.execute("SELECT * FROM users WHERE email = ?", email)

        if len(rows) == 1:
            return render_template("apology.html", message="You are already registered for an account.", route="/register")

        # Hashes the password for privacy
        password = generate_password_hash(request.form.get("password"))
        phone = request.form.get("phone")
        first = request.form.get("first")
        last = request.form.get("last")

        dt_string = datetime.now().strftime("%m/%d/%Y %H:%M")

        # Inserts their information, including last active
        db.execute("INSERT INTO users (first_name,last_name,email, hash,phone,lastactive) VALUES(?,?,?,?,?,?)",
                   first, last, email, password, phone, dt_string)

        rows = db.execute("SELECT * FROM users WHERE email = :email", email=request.form.get("email"))
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


# Generates profile update page
@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Allow a user to create and update his/her profile"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Insert all the values from the form into the appropriate slots in the database
        email = request.form.get("email")
        phone = request.form.get("phone")
        location = request.form.get("location")
        year = request.form.get("year")
        myclass = request.form.get("class")
        bio = request.form.get("bio")
        concentration = request.form.get("concentration")
        length = request.form.get("length")
        preference = request.form.get("preference")

        newclass = False

        currentclass = db.execute("SELECT class FROM users WHERE user_id = :user", user=session["user_id"])[0]["class"]

        # Checks if they have added a new class --  you don't want to update matches if they just change their email, for ex.
        if currentclass is None and myclass is not None:
            newclass = True

        # Checks if the class is changed from the old one -- then, you'll have to do some deletions
        if currentclass != myclass:
            newclass = True
            changeclass = True

        db.execute("UPDATE users SET email=:email, preference=:preference, phone=:phone, location=:location,class=:myclass, bio=:bio,year=:year, concentration=:concentration, length=:length WHERE user_id = :user",
                   email=email, phone=phone, location=location, year=year, preference=preference, myclass=myclass, bio=bio, concentration=concentration, length=length, user=session["user_id"])

        # Check for all profiles that match your class and create new rows in the SQL table "matches", set to matchstatus = 0

        if newclass:

            # Deletes previous failed or unseen matches. Keep successful matches, because they could be useful
            if changeclass:
                db.execute("DELETE FROM matches WHERE id_matcher = :user_id AND matchstatusmatcher != 1 AND class != :myclass",
                           user_id=session["user_id"], myclass=myclass)
                db.execute("DELETE FROM matches WHERE id_matchee = :user_id AND matchstatusmatcher != 1 AND class != :myclass",
                           user_id=session["user_id"], myclass=myclass)

            others = db.execute("SELECT user_id FROM users WHERE class = :myclass", myclass=myclass)

            for i in others:
                id_matcher = i["user_id"]
                id_matchee = session["user_id"]
                matchstatusmatcher = 0
                matchstatusmatchee = 0

                # Inserts all the new rows into the table
                if id_matcher != id_matchee:
                    db.execute("INSERT INTO matches (id_matcher, id_matchee, matchstatusmatcher, matchstatusmatchee,class) VALUES (?,?,?,?,?)",
                               id_matcher, id_matchee, matchstatusmatcher, matchstatusmatchee, myclass)

                # Deletes potential repeat matches
                db.execute("DELETE FROM matches WHERE id_matcher = :id_matcher AND id_matchee = :id_matchee",
                           id_matcher=session["user_id"], id_matchee=i["user_id"])

        return redirect("/dashboard")

    else:
        info = db.execute("SELECT * FROM users WHERE user_id = :user", user=session["user_id"])

        # Using pytz library to get a list of all timezones
        timezones = pytz.all_timezones

        # Redirect user to login form
        return render_template("profile.html", info=info[0], timezones=timezones)


# Generating the cards that show up when you search for Buddies
@app.route("/buddyfinder")
def buddyfinder():
    """Use SQL data to generate profile cards based on those you haven't seen"""

    # Accounts for any cards that were "left over" that might screw up later
    db.execute("UPDATE matches SET currentcard = 0")

    # Select randomly one non seen match and display information
    person = db.execute("SELECT id_matchee FROM matches WHERE id_matcher = :user AND matchstatusmatcher = 0",
                        user=session["user_id"])
    other = db.execute("SELECT id_matcher FROM matches WHERE id_matchee = :user AND matchstatusmatchee = 0",
                       user=session["user_id"])

    selection = 0
    other_is_matchee = False

    if len(person) > 0:
        selection = person[0]["id_matchee"]
        other_is_matchee = True

    elif len(other) > 0:
        selection = other[0]["id_matcher"]

    # If there are no users you can match with, you get a special version of the apology page
    else:
        return render_template("apology.html", other=True, message="There are no other students in your class. Wait a few days for more users to join!", route="/dashboard")

    cardinfo = db.execute("SELECT * FROM users WHERE user_id = :selection", selection=selection)

    # Again, need to account for both possibilities
    if other_is_matchee:
        db.execute("UPDATE matches SET currentcard = 1 WHERE id_matchee = :selection AND id_matcher = :user",
                   selection=selection, user=session["user_id"])

    else:
        db.execute("UPDATE matches SET currentcard = 1 WHERE id_matcher = :selection AND id_matchee = :user",
                   selection=selection, user=session["user_id"])

    # Render profile with the info
    return render_template("buddyfinder.html", cardinfo=cardinfo[0])


@app.route("/apology")
def apology():
    """Show an apology page and say what went wrong"""
    return render_template("apology.html", message="There was an error", route="/")


@app.errorhandler(404)
def page_not_found(e):
    # Note that we set the 404 status explicitly
    return render_template('apology.html', message="The page you were looking for does not exist.", route="/"), 404


@app.errorhandler(500)
def server_side_error(e):
    return render_template('apology.html', message="Our servers are confused or we made a coding mistake.", route="/"), 500


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")