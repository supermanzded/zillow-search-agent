import schedule
from zillow import ZillowClient
from report import generate_excel_report
from emailer import send_email

def job():
    client = ZillowClient()
    listings = client.search_properties()
    filepath = generate_excel_report(listings)
    send_email(filepath)

schedule.every().tuesday.at("09:30").do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
