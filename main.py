print("Starting Main")
import os
from dotenv import load_dotenv

print("Loading environment...")
load_dotenv()

EMAIL_USER = os.getenv("GMAIL_USER")
EMAIL_PASS = os.getenv("GMAIL_PASS")

print("Email credentials loaded.")

import schedule
from zillow import ZillowClient
from report import generate_excel_report
from emailer import send_email

def job():
    print("Starting Zillow job...")

    client = ZillowClient()
    print("ZillowClient initialized.")

    listings = [
    {"address": "123 Test Ave", "price": "$345,000", "units": 2},
    {"address": "456 Example Blvd", "price": "$298,000", "units": 3},
]

    filepath = generate_excel_report(listings)
    print(f"Report generated: {filepath}")

    send_email(filepath, EMAIL_USER, EMAIL_PASS)
    print("Email sent successfully.")

if __name__ == "__main__":
    print("Running Zillow report job now...")
    job()
    print("Zillow job completed.")
