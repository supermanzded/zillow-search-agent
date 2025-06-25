import os
import requests
from typing import List, Dict

class ZillowClient:
    """Fetch active multi‑family *for‑sale* listings near Sebring, FL using the Realtor16 API (apimaker)."""

    BASE_URL = "https://realtor-search.p.rapidapi.com/properties/search-buy?location=city%3A%20Orlando%2C%20Florida&sortBy=relevance&expandSearchArea=50&propertyType=multi_family&prices=200000%2C400000&bedrooms=2&bathrooms=1"

    def __init__(self):
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            raise RuntimeError("RAPIDAPI_KEY environment variable not set")

        self.headers = {
            "X-RapidAPI-Key": key,
            "X-RapidAPI-Host": "realtor-search.p.rapidapi.com",
        }
        print("ZillowClient (Realtor16 for‑sale API) ready.")


        resp = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print("❌ HTTP", resp.status_code, resp.text[:250])
        resp.raise_for_status()

        # Realtor16 returns an object with "data" key holding a list of property dicts
        return resp.json().get("data", [])

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
