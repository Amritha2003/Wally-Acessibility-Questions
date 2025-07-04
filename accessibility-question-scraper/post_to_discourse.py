# post_to_discourse.py
import requests
import time
import schedule

DISCOURSE_API_KEY = "1bc89c7022bc1c0e4b3a60e1d93b920f017d0541053ab60bc57e6e8a9c42a005"
DISCOURSE_API_USER = "Amritha_Arun"  # or your admin username
DISCOURSE_URL = "https://forum.wallyax.com/c/wcag-markup/17"

def post_question(title, content):
    data = {
        "title": title,
        "raw": content,
        "category": 17,  # Replace with your category ID
    }
    headers = {
        "Api-Key": DISCOURSE_API_KEY,
        "Api-Username": DISCOURSE_API_USER,
        "Content-Type": "application/json"
    }
    r = requests.post(f"{DISCOURSE_URL}/posts.json", json=data, headers=headers)
    if r.status_code == 200:
        print(f"✅ Posted: {title}")
    else:
        print(f"❌ Failed to post: {title} -- {r.text}")

def run_scraper_and_post():
    print("Scheduled job running...")
    # rest of your code...

while True:
    schedule.run_pending()
    time.sleep(1)  # Check every second instead of every minute
