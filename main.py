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

class ZillowClient:
    def __init__(self):
        self.host = os.getenv("RAPIDAPI_HOST")
        self.key = os.getenv("RAPIDAPI_KEY")
        if not self.host or not self.key:
            raise ValueError("RAPIDAPI_HOST or RAPIDAPI_KEY not set in environment variables.")
        self.base_url = f"https://{self.host}"
        self.session = requests.Session()
        self.session.headers.update({
            "x-rapidapi-host": self.host,
            "x-rapidapi-key": self.key
        })

    def fetch_listings(self, latitude=28.5383, longitude=-81.3792, radius=50, home_type="Multi-family", max_pages=5):
        """Fetch listings using the /search/bycoordinates endpoint."""
        all_listings = []

        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/search/bycoordinates"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
                "page": page,
                "sortOrder": "Homes_for_you",
                "listingStatus": "For_Sale",
                "homeType": home_type
            }

            try:
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    listings = data.get("listings") or []
                    if not listings:
                        break  # No more results
                    all_listings.extend(listings)
                    time.sleep(1)  # Avoid rate limits
                else:
                    print(f"⚠️ Attempt {page} failed - Status: {response.status_code}, Message: {response.text}")
                    time.sleep(5)
            except Exception as e:
                print(f"❌ Request error: {e}")
                break

        return all_listings

def send_email(subject: str, body: str, attachment_path: str, to_email: str) -> None:
    """Send an email with optional attachment via Gmail."""
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")

    if not gmail_user or not gmail_pass:
        print("❌ Email credentials not set (GMAIL_USER / GMAIL_PASS).")
        return

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def job() -> None:
    print("🚀 Starting Zillow Report Job (Orlando Duplex Search)")
    try:
        client = ZillowClient()
    except ValueError as e:
        print(f"❌ {e}")
        return

    print(f"📂 Using RapidAPI Host: {os.getenv('RAPIDAPI_HOST')}")

    # Fetch listings around Orlando, 50 mile radius, duplex/multi-family homes
    listings = client.fetch_listings(
        latitude=28.5383, 
        longitude=-81.3792, 
        radius=50, 
        home_type="Multi-family", 
        max_pages=5
    )

    if not listings:
        print("⚠️  No listings retrieved, skipping report generation.")
        return

    print(f"✅ Total listings retrieved: {len(listings)}")
    filepath = generate_excel_report(listings)

    if filepath:
        subject = "Weekly Orlando Duplex Zillow Report"
        body = f"Attached is the latest Zillow report with {len(listings)} duplex/multi-family listings within 50 miles of Orlando, FL."
        recipient = os.getenv("REPORT_RECIPIENT") or os.getenv("GMAIL_USER")
        send_email(subject, body, filepath, recipient)
    else:
        print("⚠️  Excel file not generated. Email skipped.")

if __name__ == "__main__":
    job()
