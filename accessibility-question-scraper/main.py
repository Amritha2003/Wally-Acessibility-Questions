# main.py
from scrape_questions import get_all_questions, fetch_stackoverflow_questions_api, get_category_for_question
from post_to_discourse import post_question
import requests
from datetime import datetime, timedelta
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from ses import send_email

STACK_OVERFLOW_TAGS = [
    "accessibility", "a11y", "accessible", "inclusive-design", "assistive-technology", "aria", "aria-label", "WCAG", "ADA",
    "section-508", "en-301-549", "eaa", "compliance", "accessibility-testing", "vpat", "audit", "screen-reader", "screenreader",
    "voiceover", "talkback", "nvda", "jaws", "chromevox", "keyboard-navigation"
]

CATEGORY_KEYWORDS = {
    16: ["accessibility", "screen reader", "a11y", "inclusive design"],  # Accessibility Advocacy
    15: ["audit", "accessibility testing", "VPAT"],                      # Accessibility Audit Guide
    19: ["voiceover", "VoiceOver","accessibility"],                                      # voiceover accessibility
    17: ["wcag", "WCAG","accessibility"],                                                # WCAG Markup
    21: ["scanning", "compliance","accessibility"],                                      # Accessibility Scanning
    14: ["ADA", "Section 508", "EN 301 549", "EAA","accessibility"],                     # ADA Compliance Workflow
    20: ["screen reader", "screenreader", "JAWS", "NVDA", "ChromeVox"],  # screen reader
}

DEFAULT_CATEGORY_ID = 16  # Set this to a valid category ID for your forum

EMAIL_FROM = "notifications@fsgarage.in"
EMAIL_TO = "aarun@fleetstudio.com"
EMAIL_SUBJECT = "Daily Accessibility Questions"
EMAIL_PASSWORD = "qqup qswd rcxc wmkw"  # Use an app password if using Gmail

def fetch_stackoverflow_questions():
    url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "creation",
        "tagged": "accessibility",  # or any tag you want
        "site": "stackoverflow"
    }
    res = requests.get(url, params=params)
    data = res.json()
    results = []
    for item in data.get("items", []):
        title = item["title"]
        link = item["link"]
        results.append((title, link))
    return results

def fetch_stackoverflow_questions_api():
    results = []
    seen_links = set()
    fromdate = int((datetime.utcnow() - timedelta(days=1)).timestamp())  # last 24h
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

def get_category_for_question(title, tags):
    title_lower = title.lower()
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower or kw.lower() in [t.lower() for t in tags]:
                return category_id
    return None

"""def send_email(body):
    msg = MIMEText(body, "plain")
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
"""
def run_scraper_and_email():
    questions = fetch_stackoverflow_questions_api()
    body = "Scraped questions:\n\n"
    for i, (title, link, tags) in enumerate(questions, 1):
        body += f"{i}. {title}\n   {link}\n   Tags: {', '.join(tags)}\n\n"
    subject="Daily Accessibility Questions"
    send_email(subject,body)
    print("Email sent!")

# Schedule for 10:00 AM every day
now = datetime.now()
scheduled_time = (now + timedelta(minutes=1)).strftime("%H:%M")
schedule.every().day.at(scheduled_time).do(run_scraper_and_email)
print(f"Automation started. Will run at {scheduled_time}...")
while True:
    schedule.run_pending()
    time.sleep(60)
