from scrape_questions import get_all_questions, get_category_for_question
from post_to_discourse import post_question
import requests
from datetime import datetime, timedelta
import schedule
import time
from ses import send_email
import re
from bs4 import BeautifulSoup

STACK_OVERFLOW_TAGS = [
    "accessibility", "a11y", "accessible", "inclusive-design", "assistive-technology", "aria", "aria-label", "WCAG", "ADA",
    "section-508", "en-301-549", "eaa", "compliance", "accessibility-testing", "vpat", "audit", "screen-reader", "screenreader",
    "voiceover", "talkback", "nvda", "jaws", "chromevox", "keyboard-navigation"
]

CATEGORY_KEYWORDS = {
    16: ["accessibility", "screen reader", "a11y", "inclusive design"],
    15: ["audit", "accessibility testing", "VPAT"],
    19: ["voiceover", "VoiceOver", "accessibility"],
    17: ["wcag", "WCAG", "accessibility"],
    21: ["scanning", "compliance", "accessibility"],
    14: ["ADA", "Section 508", "EN 301 549", "EAA", "accessibility"],
    20: ["screen reader", "screenreader", "JAWS", "NVDA", "ChromeVox"],
}

EMAIL_FROM = "notifications@fsgarage.in"
EMAIL_TO = "aarun@fleetstudio.com"
EMAIL_SUBJECT = "Daily Accessibility Questions"

def fetch_stackoverflow_questions_api():
    results = []
    seen_links = set()
    fromdate = int((datetime.utcnow() - timedelta(days=1)).timestamp())
    for tag in STACK_OVERFLOW_TAGS:
        url = "https://api.stackexchange.com/2.3/questions"
        params = {
            "order": "desc",
            "sort": "creation",
            "tagged": tag,
            "site": "stackoverflow",
            "pagesize": 20,
            "fromdate": fromdate
        }
        res = requests.get(url, params=params)
        data = res.json()
        for item in data.get("items", []):
            title = item["title"]
            link = item["link"]
            tags = item["tags"]
            if link not in seen_links:
                results.append((title, link, tags))
                seen_links.add(link)
    return results

def fetch_stackexchange_questions():
    results = []
    seen_links = set()
    fromdate = int((datetime.utcnow() - timedelta(days=1)).timestamp())
    for tag in STACK_OVERFLOW_TAGS:
        url = "https://api.stackexchange.com/2.3/questions"
        params = {
            "order": "desc",
            "sort": "creation",
            "tagged": tag,
            "site": "stackexchange",
            "pagesize": 20,
            "fromdate": fromdate
        }
        res = requests.get(url, params=params)
        data = res.json()
        for item in data.get("items", []):
            title = item["title"]
            link = item["link"]
            tags = item["tags"]
            if link not in seen_links:
                results.append((title, link, tags))
                seen_links.add(link)
    return results

def fetch_reddit_questions():
    headers = {'User-Agent': 'Mozilla/5.0'}
    subreddits = ['accessibility', 'a11y', 'blind']
    results = []
    seen_links = set()

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit=10"
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            continue
        data = res.json()
        for post in data.get("data", {}).get("children", []):
            post_data = post["data"]
            title = post_data["title"]
            link = "https://www.reddit.com" + post_data["permalink"]
            tags = [sub]
            if link not in seen_links:
                results.append((title, link, tags))
                seen_links.add(link)
    return results

def fetch_quora_questions():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://www.quora.com/topic/Accessibility-1/questions'
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return []
    soup = BeautifulSoup(res.text, 'html.parser')
    results = []
    seen_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        title = a.get_text(strip=True)
        if not title or not href:
            continue
        if '/question/' not in href:
            continue
        link = f'https://www.quora.com{href}' if href.startswith('/') else href
        if link not in seen_links:
            results.append((title, link, ['quora']))
            seen_links.add(link)
    return results

def get_category_for_question(title, tags):
    title_lower = title.lower()
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower or kw.lower() in [t.lower() for t in tags]:
                return category_id
    return None

def run_scraper_and_email():
    so_questions = fetch_stackoverflow_questions_api()
    se_questions = fetch_stackexchange_questions()
    reddit_questions = fetch_reddit_questions()
    quora_questions = fetch_quora_questions()

    all_questions = so_questions + se_questions + reddit_questions + quora_questions

    body = "Scraped questions:<br><br>"
    for i, (title, link, tags) in enumerate(all_questions, 1):
        body += (
        f"{i}. {title}<br>"
        f"&nbsp;&nbsp;{link}<br>"
        f"&nbsp;&nbsp;Tags: {', '.join(tags)}<br><br>"
    )

    send_email(EMAIL_SUBJECT, body)
    print("Email sent!")

now = datetime.now()
scheduled_time = (now + timedelta(minutes=1)).strftime("%H:%M")
schedule.every().day.at(scheduled_time).do(run_scraper_and_email)
print(f"Automation started. Will run at {scheduled_time}...")

while True:
    schedule.run_pending()
    time.sleep(60)
