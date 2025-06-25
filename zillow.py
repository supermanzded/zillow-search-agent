import os
import requests
from typing import List, Dict

class ZillowClient:
    """Fetch active multi‑family listings using Realtor16 API (apimaker)"""

    BASE_URL = "https://realtor16.p.rapidapi.com/search/forrent/coordinates"
    HOST     = "realtor16.p.rapidapi.com"
    LAT, LON = 27.4956, -81.4409   # Sebring, FL
    RADIUS   = 105

    def __init__(self):
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            raise RuntimeError("RAPIDAPI_KEY environment variable not set")

        self.headers = {
            "X-RapidAPI-Key":  key,
            "X-RapidAPI-Host": self.HOST,
        }
        print("ZillowClient (Realtor16 API) ready.")

    def _fetch(self, offset: int, limit: int = 100) -> List[Dict]:
        params = {
            "latitude":   self.LAT,
            "longitude":  self.LON,
            "radius":     self.RADIUS,
            "offset":     offset,
            "limit":      limit,
            "beds_min":   2,
            "baths_min":  1,
            "price_min":  200000,
            "price_max":  400000,
            "property_type": "multi_family",
        }

        resp = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print("❌ HTTP", resp.status_code, resp.text[:200])
        resp.raise_for_status()

        data = resp.json()
        return data.get("data", [])  # Adjust based on actual response format

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
