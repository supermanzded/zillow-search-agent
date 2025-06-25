import os
import pandas as pd
from zillow import ZillowClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email(subject, body, attachment_path, to_email):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")

    if not gmail_user or not gmail_pass:
        print("Email credentials not set")
        return

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def save_listings_to_excel(listings, filepath):
    if not listings:
        print("No listings to save.")
        return False

    # Flatten relevant fields into a DataFrame; adjust keys based on API response structure
    rows = []
    for item in listings:
        row = {
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
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_excel(filepath, index=False)
    print(f"Listings saved to {filepath}")
    return True

def job():
    print("Starting Main")
    client = ZillowClient()
    listings = client.search_properties()

    if not listings:
        print("No listings retrieved, skipping report generation.")
        return

    excel_path = "zillow_listings.xlsx"
    saved = save_listings_to_excel(listings, excel_path)

    if saved:
        subject = "Weekly Zillow Property Report"
        body = f"Attached is the latest report with {len(listings)} listings."
        recipient = os.getenv("REPORT_RECIPIENT", os.getenv("GMAIL_USER"))  # Fallback to sender if not set
        send_email(subject, body, excel_path, recipient)
    else:
        print("No data to write. Excel file will not be generated.")
        print("No email sent — no data to report.")

if __name__ == "__main__":
    job()
