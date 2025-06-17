# zillow.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

class ZillowClient:
    def search_properties(self):
        url = "https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/"

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        # Wait for listings to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test='property-card']"))
            )
        except Exception as e:
            print("Timeout waiting for listings to load:", e)
            driver.quit()
            return []

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        listings = []
        for card in soup.select("[data-test='property-card']"):
            try:
                address = card.select_one("address").get_text(strip=True)
                price = card.select_one("[data-test='property-card-price']").get_text(strip=True)
                listings.append({
                    "address": address,
                    "price": price,
                    "units": "N/A"  # Update later if unit info becomes available
                })
            except Exception as e:
                continue  # Skip if any field is missing

        return listings
