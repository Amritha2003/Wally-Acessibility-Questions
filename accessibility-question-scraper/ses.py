import boto3
from dotenv import load_dotenv
import os

load_dotenv()



def send_email(subject, body_html_content):
    sender = os.getenv("SENDER_EMAIL")
    recipients_raw = os.getenv("RECIPIENT_EMAILS", "")
    ccs_raw = os.getenv("CC_EMAILS", "")

    if not sender:
        raise ValueError("EMAIL_FROM must be set in .env")
    if not recipients_raw:
        raise ValueError("RECIPIENT_EMAILS must be set in .env")

    recipients = [email.strip() for email in recipients_raw.split(',') if email.strip()]
    ccs = [email.strip() for email in ccs_raw.split(',') if email.strip()]

    destination = {'ToAddresses': recipients}
    if ccs:
        destination['CcAddresses'] = ccs

    ses_client = boto3.client(
        'ses',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

    try:
        response = ses_client.send_email(
            Source=sender,
            Destination=destination,
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html_content}}
            }
        )
    except Exception as e:
        raise
    return response 