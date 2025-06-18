# zillow.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class ZillowClient:
    def __init__(self):
        print("ZillowClient initialized.")

    def search_properties(self):
        print("Starting property search...")

        url = (
            "https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/"
            "200000-400000_price/105.0-mile_radius/central-ac/"
        )

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # ✅ This ensures the actual ChromeDriver binary is used
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(url)

            # Wait until listings are loaded
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test='property-card']"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")

            listings = []
            for card in soup.select("[data-test='property-card']"):
                try:
                    address = card.select_one("address").get_text(strip=True)
                    price = card.select_one("[data-test='property-card-price']").get_text(strip=True)
                    listings.append({
                        "address": address,
                        "price": price,
                        "units": "N/A"
                    })
                except Exception as e:
                    continue  # Ignore cards with missing info

            print(f"Found {len(listings)} listings.")
            return listings

        except Exception as e:
            print("Error during Zillow scraping:", str(e))
            return []

        finally:
            driver.quit()
