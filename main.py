import os
import pandas as pd
from zillow import ZillowClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


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


# ─────────────────────────────────────────── Excel helper
def save_listings_to_excel(listings, filepath: str) -> bool:
    if not listings:
        print("⚠️  No listings to save.")
        return False

    # ── NEW: show a sample in the logs
    print("First 3 listings sample (raw JSON objects):")
    for listing in listings[:3]:
        print(listing)

    rows = []
    for item in listings:
        rows.append(
            {
                "Price": item.get("price"),
                "Beds": item.get("beds"),
                "Baths": item.get("baths"),
                "Address": item.get("address", {}).get("line"),
                "City": item.get("address", {}).get("city"),
                "State": item.get("address", {}).get("state_code"),
                "ZIP": item.get("address", {}).get("postal_code"),
                "Property Type": item.get("prop_type"),
                "Listing URL": item.get("rdc_web_url"),
            }
        )

    pd.DataFrame(rows).to_excel(filepath, index=False)
    print(f"✅ Listings saved to {filepath}")
    return True


# ─────────────────────────────────────────── Main job
def job() -> None:
    print("Starting Main")

    client = ZillowClient()
    listings = client.search_properties()

    if not listings:
        print("No listings retrieved, skipping report generation.")
        return

    excel_path = "zillow_listings.xlsx"
    if save_listings_to_excel(listings, excel_path):
        subject = "Weekly Zillow Property Report"
        body = f"Attached is the latest report with {len(listings)} listings."
        recipient = os.getenv("REPORT_RECIPIENT") or os.getenv("GMAIL_USER")
        send_email(subject, body, excel_path, recipient)
    else:
        print("No Excel file created; email not sent.")


if __name__ == "__main__":
    job()
