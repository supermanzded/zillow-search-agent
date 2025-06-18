import os
import schedule
import time
from dotenv import load_dotenv
from zillow import ZillowClient
from report import generate_excel_report
from emailer import send_email

print("Starting Main")

# Load environment variables
print("Loading environment...")
load_dotenv()
EMAIL_USER = os.getenv("GMAIL_USER")
EMAIL_PASS = os.getenv("GMAIL_PASS")
print("Email credentials loaded.")

def job():
    print("Starting Zillow job...")
    client = ZillowClient()
    print("ZillowClient initialized.")

    listings = client.search_properties()
    print(f"Retrieved {len(listings)} listings.")

    filepath = generate_excel_report(listings)
    if filepath:
        send_email(filepath, EMAIL_USER, EMAIL_PASS)
        print("Email sent successfully.")
    else:
        print("No email sent — no data to report.")

if __name__ == "__main__":
    print("Scheduling Zillow job for every Tuesday at 09:30 AM...")
    schedule.every().tuesday.at("09:30").do(job)

    # Run once immediately for test/debug
    job()

    # Only enter infinite loop if NOT running inside GitHub Actions
    if os.getenv("GITHUB_ACTIONS") != "true":
        print("Starting local schedule loop...")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        print("Detected GitHub Actions environment — skipping loop.")
