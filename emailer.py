import smtplib
from email.message import EmailMessage

def send_email(filepath, user, password):
    msg = EmailMessage()
    msg["Subject"] = "Weekly Zillow Report"
    msg["From"] = user
    msg["To"] = user
    msg.set_content("Attached is your weekly Zillow report.")

    with open(filepath, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="octet-stream",
            filename="zillow_report.xlsx"
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.ehlo()  # optional but good practice
            smtp.login(user, password)
            smtp.send_message(msg)
        print("✅ Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"❌ Failed to send email: {e}")
