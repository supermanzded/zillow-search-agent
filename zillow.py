from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time

class ZillowClient:
    def search_properties(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # Load Sebring, FL multi-family properties
        url = "https://www.zillow.com/sebring-fl/multi-family_att/"
        driver.get(url)

        time.sleep(5)  # Wait for JS to load content

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        listings = []

        for card in soup.select("article"):
            try:
                address = card.select_one("address").text
                price = card.select_one("span[data-test='property-card-price']").text
                listings.append({
                    "address": address,
                    "price": price,
                    "units": "N/A"  # Unit count not directly available
                })
            except Exception:
                continue

        return listings

        return listings
