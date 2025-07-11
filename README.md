Weekly Real Estate Listings Tracker

This project automates the weekly search, collection, and reporting of real estate listings within a user-defined market. Users can specify criteria such as the number of bedrooms/bathrooms (e.g., 3 bed / 3 bath) and a price range (e.g., $300K–$450K), and the script will search for matching properties within a 50-mile radius of a target location.

🔍 Key Features:
Automated Web Scraping: Collects fresh housing data from real estate websites based on user-defined search parameters.

Smart Comparison & Updates: Uses property address as a unique identifier to:

Add new listings not previously seen

Update existing entries (e.g., price reductions or status changes)

Excel Reporting: Generates a clean, structured Excel spreadsheet containing:

Property details

Pricing and status information

A clickable URL for each listing, allowing users to view it directly online

Email Automation: Automatically sends the updated Excel file to the user via email each week.

🛠 Tech Stack:
Python

BeautifulSoup / Requests (for web scraping)

Pandas (for data processing)

openpyxl / xlsxwriter (for Excel output)

smtplib / email (for sending email attachments)

Optional: schedule / cron for weekly execution

This tool is ideal for anyone looking to monitor housing market trends, track listing changes, or automate their real estate scouting process.
