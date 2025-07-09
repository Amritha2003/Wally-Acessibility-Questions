import logging
import os
from scrape_questions import fetch_stackoverflow_questions_api
from ses import send_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Lambda event: {event}")
    logger.info(f"Lambda context: {context}")
    questions = fetch_stackoverflow_questions_api()
    body = "Scraped questions:\n\n"
    for i, (title, link, tags) in enumerate(questions, 1):
        body += f"{i}. {title}\n   {link}\n   Tags: {', '.join(tags)}\n\n"
    subject = "Daily Accessibility Questions"
    send_email(subject, body)
    logger.info("Email sent!")
    return {"status": "success", "questions_sent": len(questions)} 