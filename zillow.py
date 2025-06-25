import os
import requests
from typing import List, Dict

class ZillowClient:
    """Fetch active multi‑family listings from Realtor Search API."""

    BASE_URL = "https://realtor-search.p.rapidapi.com/properties/list-for-sale"
    HOST     = "realtor-search.p.rapidapi.com"
    LAT, LON = 27.4956, -81.4409   # Sebring, FL
    RADIUS   = 105                 # miles

    def __init__(self):
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            raise RuntimeError("RAPIDAPI_KEY environment variable not set")

        self.headers = {
            "X-RapidAPI-Key":  key,
            "X-RapidAPI-Host": self.HOST,
        }
        print("ZillowClient (Realtor Search API) ready.")

    # ──────────────────────────────────────────────── helpers
    def _fetch(self, offset: int, limit: int = 100) -> List[Dict]:
        params = {
            "lat":        self.LAT,
            "lon":        self.LON,
            "radius":     self.RADIUS,
            "limit":      limit,
            "offset":     offset,
            "price_min":  200_000,
            "price_max":  400_000,
            "beds_min":   2,
            "baths_min":  1,
            "property_type": "multi_family",
            "sort":       "newest",
        }

        resp = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print("❌ HTTP", resp.status_code, resp.text[:200])
        resp.raise_for_status()

        # Realtor Search response structure
        data = resp.json().get("data", {}).get("home_search", {})
        return data.get("results", [])

    # ──────────────────────────────────────────────── public
    def search_properties(self) -> List[Dict]:
        print("Fetching listings …")
        listings: List[Dict] = []
        offset, batch_size = 0, 100

        while True:
            batch = self._fetch(offset, batch_size)
            if not batch:
                break
            listings.extend(batch)
            if len(batch) < batch_size:
                break
            offset += batch_size

        print(f"✅ Total listings fetched: {len(listings)}")
        return listings

