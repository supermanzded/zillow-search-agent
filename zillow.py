# zillow.py

import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def clear_wdm_cache():
    wdm_cache_dir = os.path.expanduser("~/.wdm")
    if os.path.exists(wdm_cache_dir):
        shutil.rmtree(wdm_cache_dir)
        print("webdriver-manager cache cleared.")

class ZillowClient:
    def search_properties(self):
        clear_wdm_cache()
        start = time.time()
        url = "https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/"
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        print(f"Starting ChromeDriver at {time.strftime('%X')}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"ChromeDriver started in {time.time() - start:.2f}s")

        driver.get(url)
        print(f"Page loaded in {time.time() - start:.2f}s")

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-test='property-card']"))
            )
            print(f"Listings appeared in {time.time() - start:.2f}s")
        except Exception as e:
            print("Timeout waiting for listings to load:", e)
            driver.quit()
            return []

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        print(f"Driver quit in {time.time() - start:.2f}s")

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
            except Exception:
                continue

        print(f"Extracted {len(listings)} listings in {time.time() - start:.2f}s")
        return listings
