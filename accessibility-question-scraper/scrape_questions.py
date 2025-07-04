# scrape_questions.py
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from post_to_discourse import DISCOURSE_API_KEY, DISCOURSE_API_USER, DISCOURSE_URL

KEYWORDS = [
    "accessibility", "a11y", "accessible", "inclusive design", "assistive technology", "aria", "aria-label", "WCAG", "ADA", "Section 508", "EN 301 549", "EAA", "compliance", "accessibility testing", "VPAT", "audit", "screen reader", "screenreader", "VoiceOver", "TalkBack", "NVDA", "JAWS", "ChromeVox", "keyboard navigation",
    # Subreddits
    "r/accessibility", "r/webdev", "r/web_design", "r/frontend", "r/AskProgramming", "r/reactjs", "r/javascript", "r/UXDesign", "r/iOSProgramming", "r/androiddev",
    # Quora categories
    "Accessibility (web)", "Digital Accessibility", "Web Development", "User Experience (UX)", "Assistive Technology",
    # UX Stack Exchange tags
    "accessibility", "wcag", "aria", "inclusive-design", "screen-readers",
    # Stack Overflow tags
    "accessibility", "a11y", "aria", "screen-reader", "voiceover", "talkback"
]

CATEGORY_KEYWORDS = {
    16: ["accessibility", "screen reader", "a11y", "inclusive design"],  # Accessibility Advocacy
    15: ["audit", "accessibility testing", "VPAT"],                      # Accessibility Audit Guide
    19: ["voiceover", "VoiceOver"],                                      # voiceover accessibility
    17: ["wcag", "WCAG"],                                                # WCAG Markup
    21: ["scanning", "compliance"],                                      # Accessibility Scanning
    14: ["ADA", "Section 508", "EN 301 549", "EAA"],                     # ADA Compliance Workflow
    20: ["screen reader", "screenreader", "JAWS", "NVDA", "ChromeVox"],  # screen reader
}

def keyword_filter(text):
    return any(kw.lower() in text.lower() for kw in KEYWORDS)

def scrape_stackoverflow():
    url = "https://stackoverflow.com/questions?tab=Newest"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    
    for q in soup.select(".s-post-summary--content-title a"):
        title = q.get_text(strip=True)
        link = "https://stackoverflow.com" + str(q['href'])
        if keyword_filter(title):
            results.append((title, link))
    return results

def scrape_ux_stackexchange():
    url = "https://ux.stackexchange.com/questions?tab=Newest"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    
    for q in soup.select(".s-post-summary--content-title a"):
        title = q.get_text(strip=True)
        link = "https://ux.stackexchange.com" + str(q['href'])
        if keyword_filter(title):
            results.append((title, link))
    return results

def scrape_reddit():
    url = "https://www.reddit.com/r/web_design/new/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    
    for post in soup.select("a[href*='/r/web_design/comments']"):
        title = post.get_text(strip=True)
        href = post.get("href")
        if keyword_filter(title):
            results.append((title, f"https://www.reddit.com{href}"))
    return results

def scrape_stackoverflow_selenium():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://stackoverflow.com/questions?tab=Newest")
    time.sleep(3)  # Wait for JS to load content
    results = []
    questions = driver.find_elements(By.CSS_SELECTOR, ".s-post-summary--content-title a")
    for q in questions:
        title = q.text.strip()
        link = q.get_attribute('href')
        if keyword_filter(title):
            results.append((title, link))
    driver.quit()
    return results

def get_all_questions():
    return (
        scrape_stackoverflow() +
        scrape_ux_stackexchange() +
        scrape_reddit()
    )

def get_category_for_question(title):
    title_lower = title.lower()
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return category_id
    return None  # Or a default category ID if you want

def run_scraper_and_post():
    questions = scrape_stackoverflow_selenium()
    for title, link in questions:
        category_id = get_category_for_question(title)
        if category_id:
            post_question(title, f"Found this question: {link}", category_id)
        else:
            print(f"❌ No matching category for: {title}")

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

if __name__ == "__main__":
    questions = scrape_stackoverflow_selenium()
    with open("scraped_questions_selenium.txt", "w", encoding="utf-8") as f:
        for i, (title, link) in enumerate(questions, 1):
            f.write(f"{i}. {title}\n   {link}\n\n")
