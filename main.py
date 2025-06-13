import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("GMAIL_USER")
EMAIL_PASS = os.getenv("GMAIL_PASS")
import schedule
from zillow import ZillowClient
from report import generate_excel_report
from emailer import send_email

def job():
    client = ZillowClient()
    listings = client.search_properties()
    filepath = generate_excel_report(listings)
    send_email(filepath)

if __name__ == "__main__":
    # Run the job immediately for testing
    job()
