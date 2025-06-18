from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class ZillowClient:
    def __init__(self):
        print("ZillowClient initialized.")

    def search_properties(self):
        print("Starting property search...")

        options = Options()
        options.add_argument("--headless=new")  # Required for GitHub Actions
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # ✅ CORRECT: Automatically installs and points to the actual ChromeDriver binary
        service = Service(ChromeDriverManager().install())

        # ✅ Use standard webdriver.Chrome setup
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get("https://www.zillow.com/")
            print("Page title:", driver.title)
            # Your actual scraping logic goes here...

            listings = []  # Replace this with your real data
            return listings

        finally:
            driver.quit()
