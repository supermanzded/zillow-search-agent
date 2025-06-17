# zillow.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
        time.sleep(5)  # Give JS time to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        listings = []
        for card in soup.select("article"):
            try:
                address = card.select_one("address").text.strip()
                price = card.select_one("span[data-test='property-card-price']").text.strip()
                listings.append({
                    "address": address,
                    "price": price,
                    "units": "N/A"  # Optional: Improve if unit info is available
                })
            except Exception:
                continue

        return listings

