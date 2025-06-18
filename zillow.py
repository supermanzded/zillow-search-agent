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
import time


class ZillowClient:
    def __init__(self):
        print("ZillowClient initialized.")

    def search_properties(self):
        print("Starting property search...")

        options = Options()
        options.add_argument("--headless=new")  # For GitHub Actions
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        raw_path = ChromeDriverManager().install()
        driver_path = Path(raw_path).parent / "chromedriver"
        os.chmod(driver_path, 0o755)

        service = Service(str(driver_path))
        driver = webdriver.Chrome(service=service, options=options)

        url = "https://www.zillow.com/sebring-fl/multi-family/2-_beds/1-_baths/200000-400000_price/105.0-mile_radius/central-ac/"

        try:
            print(f"Navigating to {url}")
            driver.get(url)
            time.sleep(5)  # Allow some JS to load

            # Scroll to bottom to load lazy content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='property-card']"))
            )

            # Debug dump
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
                print("Saved page source to debug_page.html")

            driver.save_screenshot("debug_screenshot.png")
            print("Saved screenshot to debug_screenshot.png")

            print("Parsing results...")
            soup = BeautifulSoup(driver.page_source, "html.parser")
            cards = soup.select("[data-test='property-card']")
            listings = []

            for card in cards:
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

        except Exception as e:
            print(f"❌ Exception occurred: {e}")
            # Save debug files even on exception
            try:
                driver.save_screenshot("debug_screenshot.png")
                print("Saved screenshot to debug_screenshot.png (after exception)")
            except Exception as se:
                print(f"Failed to save screenshot: {se}")
            try:
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                    print("Saved page source to debug_page.html (after exception)")
            except Exception as pe:
                print(f"Failed to save page source: {pe}")
            return []

        finally:
            driver.quit()
