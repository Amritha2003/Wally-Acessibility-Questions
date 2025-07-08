# post_to_discourse.py
import requests

DISCOURSE_API_KEY = "1bc89c7022bc1c0e4b3a60e1d93b920f017d0541053ab60bc57e6e8a9c42a005"
DISCOURSE_API_USER = "Amritha_Arun"  # or your admin username
DISCOURSE_URL = "https://forum.wallyax.com"

def post_question(title, content, category_id):
    data = {
        "title": title,
        "raw": content,
        "category": category_id,
    }
    headers = {
        "Api-Key": DISCOURSE_API_KEY,
        "Api-Username": DISCOURSE_API_USER,
        "Content-Type": "application/json"
    }
    r = requests.post(f"{DISCOURSE_URL}/posts.json", json=data, headers=headers)
    if r.status_code == 200:
        print(f"✅ Posted: {title} to category {category_id}")
    else:
        print(f"❌ Failed to post: {title} -- {r.text}")
