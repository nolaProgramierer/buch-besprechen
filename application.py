import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
    greeting = "This is the index page"
    return render_template("index.html", greeting=greeting)

@app.route("/glenn")
def glenn():
    greeting = "Hello Glenn!"
    return render_template("index.html", greeting=greeting)

def bday():
    return datetime.date(3, 9, 1952)

@app.route("/about")
def about():
    greeting = "This is the 'about' page"
    title = "About"
    return render_template("about.html", greeting=greeting, title=title)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("name")
        return render_template("main.html")
    return render_template("login.html")
