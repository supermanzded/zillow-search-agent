import os
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class ZillowClient:
    def __init__(self):
        print("ZillowClient initialized.")

    def search_properties(self):
        print("Starting property search...")

        options = Options()
        options.add_argument("--headless=new")  # Headless for GitHub Actions
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Download and set correct permissions for chromedriver
        raw_path = ChromeDriverManager().install()
        driver_path = Path(raw_path).parent / "chromedriver"
        os.chmod(driver_path, 0o755)

        service = Service(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)

        try:
            # 🧭 Zillow search URL with all filters applied
            url = "https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/"
            driver.get(url)

            # ✅ Wait until listings are rendered
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.photo-cards li article"))
            )

            print("Page loaded. Parsing...")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            listings = []

            for card in soup.select("ul.photo-cards li article"):
                try:
                    address = card.select_one("address")
                    price = card.select_one("span[data-test='property-card-price']")

                    listings.append({
                        "address": address.text.strip() if address else "N/A",
                        "price": price.text.strip() if price else "N/A",
                        "units": "N/A"
                    })
                except Exception:
                    continue

            print(f"Found {len(listings)} properties.")
            return listings

        finally:
            driver.quit()
