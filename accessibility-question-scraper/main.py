# main.py
print("Script started")
print("Importing BeautifulSoup")
from bs4 import BeautifulSoup
print("Importing requests")
from scrape_questions import get_all_questions, scrape_stackoverflow_selenium, get_category_for_question, post_question
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def run_scraper_and_post():
    print("\n=== Starting scraping and posting process ===")
    try:
        print("Launching Selenium scraper...")
        options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        questions = scrape_stackoverflow_selenium()
        print(f"Total questions scraped: {len(questions)}")
        for title, link in questions:
            category_id = get_category_for_question(title)
            print(f"Processing: {title}\n  Link: {link}\n  Category: {category_id}")
            if category_id:
                post_question(title, f"Found this question: {link}", category_id)
            else:
                print(f"❌ No matching category for: {title}")
        print("=== Scraping and posting process complete ===\n")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

# Run immediately on script start
run_scraper_and_post()
