import os
from zillow import ZillowClient
from report import generate_excel_report
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib

load_dotenv()

def send_email(subject: str, body: str, attachment_path: str, to_email: str) -> None:
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
    print("🚀 Starting Zillow Report Job (API payload search)")
    client = ZillowClient()

    search_payload = {
        "city": "Orlando",
        "state_code": "FL",
        "page": 1,
        "filters": {
            "propertyType": {"type": ["multi_family"]},
            "price": {"min": 200000, "max": 400000},
            "bed": {"min": 2},
            "bath": {"min": 1}
        }
    }

    print(f"Fetching listings for {search_payload['city']}, {search_payload['state_code']} …")

    listings = client.fetch_listings(location=f"{search_payload['city']}, {search_payload['state_code']}")

    if not listings:
        print("⚠️  No listings retrieved, skipping report generation.")
        return

    print("✅ Listings data retrieved successfully.")
    filepath = generate_excel_report(listings)

    if filepath:
        subject = "Weekly Zillow Property Report"
        body = f"Attached is the latest report."
        recipient = os.getenv("REPORT_RECIPIENT") or os.getenv("GMAIL_USER")
        send_email(subject, body, filepath, recipient)
    else:
        print("⚠️  Excel file not generated. Email skipped.")

if __name__ == "__main__":
    job()
