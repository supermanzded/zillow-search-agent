from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

class ZillowClient:
    def search_properties(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        url = "https://www.zillow.com/sebring-fl/multi-family_att/"
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
        except Exception as e:
            print("Timeout waiting for listings to load:", e)

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
                    "units": "N/A"
                })
            except Exception:
                continue

        return listings
