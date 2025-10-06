import os
import time
import requests
from typing import List, Dict, Optional

class ZillowClient:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = os.getenv("RAPIDAPI_HOST")
        self.base_url = f"https://{self.api_host}"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }

        if not self.api_key or not self.api_host:
            raise ValueError("❌ Missing RAPIDAPI_KEY or RAPIDAPI_HOST in .env file")

        print(f"ZillowClient initialized with host: {self.api_host}")

    def fetch_listings(self, location: Optional[str] = None, zpid: Optional[str] = None) -> List[Dict]:
        """
        Fetch property listings using a Zillow zpid or fallback search.
        """
        if zpid:
            url = f"{self.base_url}/custom_ag/byzpid"
            params = {"zpid": zpid}
        else:
            # fallback example (if you want location search later)
            url = f"{self.base_url}/custom_ag/bylocation"
            params = {"location": location or "Orlando, FL"}

        print(f"Fetching listings from: {url}")
        listings = self._make_request(url, params)

        if not listings:
            print("⚠️  No data returned from API.")
        else:
            print(f"✅ Retrieved {len(listings) if isinstance(listings, list) else 1} listing(s).")

        # Return list of dicts, even if single object
        if isinstance(listings, dict):
            listings = [listings]
        return listings or []

    def _make_request(self, url: str, params: Dict, retries: int = 3, backoff: int = 5) -> Optional[List[Dict]]:
        """
        Make API request with retries and graceful error handling.
        """
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"⚠️  Attempt {attempt}/{retries} failed - Status: {response.status_code}, Message: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error on attempt {attempt}: {e}")

            if attempt < retries:
                wait_time = backoff * attempt
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        print("❌ Max retries reached. No results fetched.")
        return None
