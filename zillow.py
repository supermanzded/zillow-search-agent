import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "zillow-working-api.p.rapidapi.com")


class ZillowClient:
    def __init__(self):
        if not RAPIDAPI_KEY:
            raise ValueError("❌ RAPIDAPI_KEY not found in environment.")
        print("ZillowClient (Working API) initialized and ready.")

    def fetch_listings(self, location="Orlando, FL", zpid="44471319", retries=3, delay=5):
        """
        Fetch property data by Zillow Property ID (ZPID)
        You can expand this later to do real searches if the API supports it.
        """
        url = f"https://{RAPIDAPI_HOST}/custom_ag/byzpid"
        params = {"zpid": zpid}
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
        }

        for attempt in range(1, retries + 1):
            try:
                print(f"Fetching property info for ZPID={zpid} (attempt {attempt}) …")
                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    print("✅ Zillow API call successful.")
                    return [response.json()]  # wrap in list to fit 'listings' expected by main.py

                print(f"⚠️  Status {response.status_code}: {response.text}")
                time.sleep(delay * attempt)

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                time.sleep(delay * attempt)

        print("🚫 Max retries reached. No data retrieved.")
        return []
