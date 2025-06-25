import os
import requests
from typing import List, Dict

class ZillowClient:
    """Fetch active multi‑family *for‑sale* listings near Sebring, FL using the Realtor16 API (apimaker)."""

    BASE_URL = "https://realtor-search.p.rapidapi.com/properties/list-for-sale?latitude=27.4956&longitude=-81.4409&radius=105&limit=50&beds_min=2&baths_min=1&price_min=200000&price_max=400000&property_type=multi_family"
    HOST     = "x-rapidapi-host: realtor-search.p.rapidapi.com"
    LAT, LON = 27.4956, -81.4409   # Sebring, FL
    RADIUS   = 105                 # miles

    # user filters
    BEDS_MIN  = 2
    BATHS_MIN = 1
    PRICE_MIN = 200_000
    PRICE_MAX = 400_000
    PROP_TYPE = "multi_family"

    def __init__(self):
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            raise RuntimeError("RAPIDAPI_KEY environment variable not set")

        self.headers = {
            "X-RapidAPI-Key":  key,
            "X-RapidAPI-Host": self.HOST,
        }
        print("ZillowClient (Realtor16 for‑sale API) ready.")

    # ───────────────────────────────────────── helpers
    def _fetch(self, offset: int = 0, limit: int = 50) -> List[Dict]:
        params = {
            "latitude":     self.LAT,
            "longitude":    self.LON,
            "radius":       self.RADIUS,
            "offset":       offset,
            "limit":        limit,
            "beds_min":     self.BEDS_MIN,
            "baths_min":    self.BATHS_MIN,
            "price_min":    self.PRICE_MIN,
            "price_max":    self.PRICE_MAX,
            "property_type": self.PROP_TYPE,
        }

        resp = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print("❌ HTTP", resp.status_code, resp.text[:250])
        resp.raise_for_status()

        # Realtor16 returns an object with "data" key holding a list of property dicts
        return resp.json().get("data", [])

    # ───────────────────────────────────────── public
    def search_properties(self) -> List[Dict]:
        print("Fetching listings …")
        listings: List[Dict] = []
        offset, batch_size = 0, 50

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
