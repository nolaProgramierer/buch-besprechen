import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

a = "%"
name = "Susan"
str = a + name + a
query = str
results = db.execute("SELECT * FROM book WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author", {"isbn": query, "title": query, "author": query})

if results.rowcount == 0:
    print(f"There is no result.")
else:
    for row in results:
        print(f" { row }")
