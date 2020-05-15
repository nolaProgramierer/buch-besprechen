import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from markupsafe import escape

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if "username" in session:
        # From Flasks docs to convert to HTML safe sequence
        message = "You are logged in as %s" % escape(session["username"])
        return render_template("index.html", message=message)
    message = "Please log in"
    return render_template("index.html", message=message)

def bday():
    return datetime.date(3, 9, 1952)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Retrieve values from form
        username = request.form.get("name")
        password = request.form.get("password")
        # Query db for form entered name and password
        if db.execute("SELECT * FROM users WHERE name = :name", {"name": username}).rowcount == 0 or db.execute("SELECT * FROM users WHERE password = :password", {"password": password}).rowcount == 0:
            message = "Incorrect name or password"
            return render_template("error.html", message=message)
        else:
            message = f"Welcome back { username }."
            # Add logged in user to session
            session["username"] = username
            return render_template("index.html", message=message)

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method =="POST":
        username = request.form.get("name")
        password = request.form.get("password")
        if username == "" or password == "":
            message = "You must enter a name and password"
            return render_template("signup.html", message=message)
        else:
            # Insert form entered values into db
            db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": username, "password": password})
            db.commit()
            message = "Welcome to the website"
            # Add new user to session object
            session["username"] = username
            return render_template("index.html", message=message)
    message = "Welcome to the Sign Up page"
    return render_template("/signup.html", message = message)

@app.route("/logout")
def signout():
    username = session["username"]
    #Remove user from user session, if user isn't signed in redirected to login page
    session.pop(username, None)
    message = "You've successfully logged out"
    return render_template("login.html", message=message)

@app.route("/users")
def users():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("users.html", users=users)
