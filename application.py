import os
import requests

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
    return render_template("/signup.html", message=message)

@app.route("/logout")
def signout():
    if session["username"] is None:
        message="Please login"
        return render_template("error.html", message=message)
    username = session["username"]
    #Remove user from user session, if user isn't signed in redirected to login page
    session.pop(username, None)
    message = "You've successfully logged out"
    return render_template("login.html", message=message)

@app.route("/books", methods=["GET", "POST"])
def books():
    if request.method == "POST":
        a = "%"
        input = request.form.get("search")
        query = a + str(input) + a
        results = db.execute("SELECT * FROM book WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author", {"isbn": query, "title": query, "author": query})
        if results.rowcount == 0:
            message="There are no results in our database"
            return render_template("/books.html", message=message)
        else:
            return render_template("/books.html", results=results)
    else:
        return render_template("/books.html")

# Display information on each individual book
@app.route("/books/<int:book_id>")
def book(book_id):
    # Get book by id number
    book = db.execute("SELECT * FROM book WHERE id = :id", {"id": book_id}).fetchone()
    if book.id is None:
        return render_template("/error.html", message="No such book.", book=book)
    isbn = book.isbn
    # put this somewhere secure
    key = "5OcycK0BLM1pY3pTVqaUKQ"

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
    bookObj = res.json()
    try:
        for val in bookObj["books"]:
            rating = val["average_rating"]
            count = val["work_ratings_count"]
            print(rating)
            print(count)
    except (ValueError, KeyError, TypeErrort):
        print("JSON format error")
    return render_template("/book.html", book=book, isbn=isbn, rating=rating, count=count)

# Add review for each book
@app.route("/books/<int:book_id>", methods=["POST"])
def review(book_id):
    # Retrieve id of user from db
    username = session["username"]
    id_row = db.execute("SELECT * FROM users WHERE name = :name", {"name": username})
    for row in id_row:
        username_id = row.id
    # Check for a book review of current book with the current user's id
    if db.execute("SELECT * FROM book_review WHERE book_id = :book_id", {"book_id": book_id}).rowcount != 0 and db.execute("SELECT * FROM book_review WHERE users_id = :users_id", {"users_id": username_id}).rowcount != 0:
        return render_template("/error.html", message="You've already submitted a review for this book.")
    # Enter review from form into db
    text = request.form.get("bookReview")
    rating = request.form.get("inlineRadioOptions")
    db.execute("INSERT INTO book_review (review, rating, book_id, users_id) VALUES (:review, :rating, :book_id, :users_id)", {"review": text, "rating": rating, "book_id": book_id, "users_id": username_id})
    db.commit()
    message = "Thank you for submitting your review"
    return render_template("success.html", message=message)

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == "POST":
        # Get json object
        book_num = request.form.get("bookApi")
        # Put this somewhere safe
        key = "5OcycK0BLM1pY3pTVqaUKQ"
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": book_num})
        bookObj = res.json()
        # Extract isbn from returned json object to vars
        isbn = bookObj["books"][0]["isbn"]
        isbn13 = bookObj["books"][0]["isbn13"]
        # Check db for isbns
        if db.execute("SELECT * FROM book WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0 and db.execute("SELECT * FROM book WHERE isbn = :isbn", {"isbn": isbn13}).rowcount == 0:
            return render_template("/error.html", message="404 error")

        # Make new json obj with information from db and api request
        review_count = bookObj["books"][0]["reviews_count"]
        average_score = bookObj["books"][0]["average_rating"]
        book = db.execute("SELECT * FROM book WHERE isbn = :isbn", {"isbn": isbn}) or db.execute("SELECT * FROM book WHERE isbn = :isbn", {"isbn": isbn13})
        for row in book:
            title = row.title
            author = row.author
            year = row.year
            isbn = row.isbn
        jsonDict = {"title":title, "author":author, "year":year, "isbn":isbn, "review_count": review_count, "average_score":average_score}
        return render_template("/api.html", message=jsonDict)
    return render_template("/api.html")

@app.route("/users")
def users():
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("users.html", users=users)
