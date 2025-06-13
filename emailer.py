import smtplib
from email.message import EmailMessage

def send_email(filepath):
    msg = EmailMessage()
    msg["Subject"] = "Weekly Zillow Report"
    msg["From"] = "thtucker@gmail.com"
    msg["To"] = "thtucker@gmail.com"
    msg.set_content("Attached is your weekly Zillow report.")
    with open(filepath, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="zillow_report.xlsx")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("thtucker@gmail.com", "your_app_password_here")
        smtp.send_message(msg)
