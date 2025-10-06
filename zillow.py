import os
import time
import requests
from dotenv import load_dotenv

# ─────────────────────────────────────────── Load environment
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "zillow-working-api.p.rapidapi.com")


class ZillowClient:
    def __init__(self):
        if not RAPIDAPI_KEY:
            raise ValueError("❌ RAPIDAPI_KEY not found in environment variables.")
        print("ZillowClient (Working API) initialized and ready.")

    def fetch_listings(self, location="Orlando, FL", zpid="44471319", retries=3, delay=5):
        """
        Fetch property data using Zillow Property ID (ZPID).
        Extend later for multi-property or city-based search.
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
                    return [response.json()]  # list wrapper for report compatibility

                print(f"⚠️  Status {response.status_code}: {response.text}")
                if response.status_code == 403:
                    print("❌  API subscription issue — check RapidAPI host or plan.")
                time.sleep(delay * attempt)

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                time.sleep(delay * attempt)

        print("🚫 Max retries reached. No data retrieved.")
        return []
