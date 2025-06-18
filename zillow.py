from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
from bs4 import BeautifulSoup
import time


class ZillowClient:
    def __init__(self):
        print("ZillowClient initialized.")

    def search_properties(self):
        print("Starting property search...")

        options = Options()
        options.add_argument("--headless=new")  # Recommended for CI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Fix for GitHub Actions: point to actual driver binary
        raw_path = ChromeDriverManager().install()
        driver_path = str(Path(raw_path).parent / "chromedriver")  # Fix: use actual binary

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get("https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/")
            time.sleep(5)  # Wait for JS to load
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
