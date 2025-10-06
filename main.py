import os
import time
import requests
from dotenv import load_dotenv
from report import generate_excel_report
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib

load_dotenv()

RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
REPORT_RECIPIENT = os.getenv("REPORT_RECIPIENT") or GMAIL_USER

# Parameters for Orlando duplex search
SEARCH_PARAMS = {
    "latitude": 28.5383,
    "longitude": -81.3792,
    "radius": 50,  # miles
    "page": 1,
    "sortOrder": "Homes_for_you",
    "listingStatus": "For_Sale",
    "bed_min": "No_Min",
    "bed_max": "No_Max",
    "bathrooms": "Any",
    "homeType": "Multi-family",  # duplexes
    "maxHOA": "Any",
    "listingType": "By_Agent",
    "listingTypeOptions": "Agent listed,New Construction,Fore-closures,Auctions",
    "parkingSpots": "Any",
    "mustHaveBasement": "No",
    "daysOnZillow": "Any",
    "soldInLast": "Any",
}

HEADERS = {
    "x-rapidapi-host": RAPIDAPI_HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}


def fetch_listings(params: dict, max_retries: int = 3, delay: int = 5) -> list:
    url = f"https://{RAPIDAPI_HOST}/search/bycoordinates"
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("searchResults", [])
                print(f"✅ Retrieved {len(results)} listings.")
                return results
            else:
                print(f"⚠️ Attempt {attempt} failed - Status: {response.status_code}, Message: {response.text}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt} exception: {e}")
        time.sleep(delay * attempt)
    print("❌ Max retries reached. No results fetched.")
    return []


def send_email(subject: str, body: str, attachment_path: str, to_email: str) -> None:
    if not GMAIL_USER or not GMAIL_PASS:
        print("❌ Email credentials not set (GMAIL_USER / GMAIL_PASS).")
        return

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def job() -> None:
    print("🚀 Starting Zillow Report Job (Orlando Duplex Search)")
    listings = fetch_listings(SEARCH_PARAMS)

    if not listings:
        print("⚠️  No listings retrieved, skipping report generation.")
        return

    # Generate Excel report
    filepath = generate_excel_report(listings)
    if filepath:
        subject = f"Weekly Zillow Orlando Duplex Report ({len(listings)} listings)"
        body = "Attached is the latest Zillow report for duplexes in Orlando."
        send_email(subject, body, filepath, REPORT_RECIPIENT)
    else:
        print("⚠️  Excel file not generated. Email skipped.")


if __name__ == "__main__":
    job()
