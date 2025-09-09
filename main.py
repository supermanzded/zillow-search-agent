import os
from zillow import ZillowClient
from report import generate_excel_report
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# ─────────────────────────────────────────── Load environment variables
load_dotenv()  # Loads GMAIL_USER, GMAIL_PASS, RAPIDAPI_KEY, REPORT_RECIPIENT from env.txt

# ─────────────────────────────────────────── Email helper
def send_email(subject: str, body: str, attachment_path: str, to_email: str) -> None:
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")

    if not gmail_user or not gmail_pass:
        print("❌ Email credentials not set (GMAIL_USER / GMAIL_PASS).")
        return

    if not to_email:
        print("❌ No recipient address supplied.")
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
            server.ehlo()
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ─────────────────────────────────────────── Main job
def job() -> None:
    print("🚀 Starting Zillow Report Job (API parameter search)")

    client = ZillowClient()

    # --------------------- Search parameters
    search_params = {
        "city": "Orlando",
        "state_code": "FL",
        "price_min": 200000,
        "price_max": 400000,
        "property_type": "multi_family",
        "beds_min": 2,
        "baths_min": 1,
        "features": ["central_air"],  # optional features
        "retries": 5,
        "delay": 3
    }

    # --------------------- Fetch listings
    listings = client.search(**search_params)

    if not listings:
        print("⚠️  No listings retrieved, skipping report generation.")
        return

    print(f"✅ Total listings fetched: {len(listings)}")

    # --------------------- Generate Excel report
    filepath = generate_excel_report(listings)

    if filepath:
        subject = "Weekly Zillow Property Report"
        body = f"Attached is the latest report with {len(listings)} listings."
        recipient = os.getenv("REPORT_RECIPIENT") or os.getenv("GMAIL_USER")
        send_email(subject, body, filepath, recipient)
    else:
        print("⚠️  Excel file not generated. Email skipped.")

if __name__ == "__main__":
    job()
