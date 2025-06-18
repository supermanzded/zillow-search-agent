import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class ZillowClient:
    def __init__(self):
        print("ZillowClient initialized.")

    def search_properties(self):
        print("Starting property search...")

        options = Options()
        options.add_argument("--headless=new")  # Required for GitHub Actions
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Get the raw path from webdriver-manager
        raw_path = ChromeDriverManager().install()

        # Fix: actual path to chromedriver binary (not a folder or notice file)
        driver_path = Path(raw_path).parent / "chromedriver"

        # 🔧 Fix permission error by making it executable
        os.chmod(driver_path, 0o755)

        service = Service(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get("https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/")
            time.sleep(5)
            print("Page loaded. Parsing...")

            soup = BeautifulSoup(driver.page_source, "html.parser")
            listings = []

            for card in soup.select("article"):
                try:
                    address = card.select_one("address").text.strip()
                    price = card.select_one("span[data-test='property-card-price']").text.strip()
                    listings.append({
                        "address": address,
                        "price": price,
                        "units": "N/A"
                    })
                except Exception:
                    continue

            print(f"Found {len(listings)} properties.")
            return listings

        finally:
            driver.quit()
