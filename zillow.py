import os
import time
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
        options.add_argument("--headless=new")  # Headless mode for CI environments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Install ChromeDriver and set permissions
        raw_path = ChromeDriverManager().install()
        driver_path = Path(raw_path).parent / "chromedriver"
        os.chmod(driver_path, 0o755)

        service = Service(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)

        try:
            url = "https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/"
            driver.get(url)

            # Wait for at least one property card to appear
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='property-card']"))
                )
            except:
                print("⚠️ Timeout: No listings found or Zillow changed layout.")
                return []

            # Handle cookie consent popup if it appears
            try:
                consent_button = driver.find_element(By.XPATH, "//button[contains(text(),'Accept')]")
                consent_button.click()
                print("Cookie consent accepted.")
                time.sleep(2)
            except Exception:
                pass

            # Allow dynamic content to load
            time.sleep(5)

            # Scroll down to bottom repeatedly to trigger lazy loading
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            # Save page source for debugging
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved page source to debug_page.html")

            # Parse listings from page source
            soup = BeautifulSoup(driver.page_source, "html.parser")
            listings = []

            for card in soup.select("[data-test='property-card']"):
                try:
                    address = card.select_one("address")
                    price = card.select_one("span[data-test='property-card-price']")
                    listings.append({
                        "address": address.text.strip() if address else "N/A",
                        "price": price.text.strip() if price else "N/A",
                        "units": "N/A"
                    })
                except Exception as e:
                    print(f"⚠️ Error parsing card: {e}")
                    continue

            print(f"✅ Found {len(listings)} properties.")
            return listings

        finally:
            driver.quit()
