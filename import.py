# Trial program to import from terminal
#import requests
#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5OcycK0BLM1pY3pTVqaUKQ", "isbns": "9781501134616"})
#print(res.json())

import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



file = open("books.csv")
reader = csv.reader(file)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO book (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
    print(f"Added { isbn }, { title }, { author } and { year } to Book table")
    db.commit();
