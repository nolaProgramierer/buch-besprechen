import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "5OcycK0BLM1pY3pTVqaUKQ", "isbns": "9781501134616"})
print(res.json())

key = "5OcycK0BLM1pY3pTVqaUKQ"
isbn = "9781501134616"


res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
bookObj = res.json()

try:
    for val in bookObj["books"]:
        rating = val["average_rating"]
        count = val["work_ratings_count"]
        print(rating)
        print(count)
except (ValueError, KeyError, TypeError):
    print("JSON format error")
print(bookObj["books"][0]["isbn"])
