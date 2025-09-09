import os
import requests
from typing import List, Dict

class ZillowClient:
    """
    Fetch active multi-family for-sale listings using Realtor Search API (RapidAPI).
    """

    BASE_URL = "https://realtor-search.p.rapidapi.com/properties/search-buy"
    HOST     = "realtor-search.p.rapidapi.com"

    # Search scope (Orlando area, within 50 miles)
    LAT = 28.5383
    LON = -81.3792
    RADIUS = 50  # miles

    # Filters
    BEDS_MIN   = 2
    BATHS_MIN  = 1
    PRICE_MIN  = 200_000
    PRICE_MAX  = 400_000
    PROP_TYPE  = "multi_family"

    def __init__(self) -> None:
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            raise RuntimeError("RAPIDAPI_KEY environment variable not set")

        self.headers = {
            "x-rapidapi-key": key,
            "x-rapidapi-host": self.HOST,
        }
        print("ZillowClient (Realtor Search API) ready.")

    def _fetch(self, offset: int = 0, limit: int = 50) -> List[Dict]:
        """Fetch one page of results."""
        params = {
            "lat": self.LAT,
            "lon": self.LON,
            "radius": self.RADIUS,
            "property_type": self.PROP_TYPE,
            "price_min": self.PRICE_MIN,
            "price_max": self.PRICE_MAX,
            "beds_min": self.BEDS_MIN,
            "baths_min": self.BATHS_MIN,
            "offset": offset,
            "limit": limit,
            "sort": "relevance"
        }

        resp = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print("❌ HTTP", resp.status_code, resp.text[:250])
        resp.raise_for_status()

        payload = resp.json()
        data = payload.get("data")
        if not data or "results" not in data:
            print("⚠️ No `results` in payload:", payload)
            return []

        return data["results"]

    def _normalize(self, raw: Dict) -> Dict:
        """Flatten one raw API record into a clean row for Excel."""
        address = raw.get("location", {}).get("address", {}).get("line")
        city = raw.get("location", {}).get("address", {}).get("city")
        state = raw.get("location", {}).get("address", {}).get("state_code")
        zipc = raw.get("location", {}).get("address", {}).get("postal_code")

        price = raw.get("list_price")
        beds = raw.get("description", {}).get("beds")
        baths = raw.get("description", {}).get("baths")
        sqft = raw.get("description", {}).get("sqft")
        url = raw.get("permalink")

        return {
            "Address": f"{address}, {city}, {state} {zipc}" if address else "N/A",
            "Price": price or "N/A",
            "Beds": beds or "N/A",
            "Baths": baths or "N/A",
            "SqFt": sqft or "N/A",
            "URL": f"https://www.realtor.com{url}" if url else "N/A"
        }

    def search_properties(self) -> List[Dict]:
        """Fetch all results and normalize them."""
        print("Fetching listings …")
        listings: List[Dict] = []
        offset, batch_size = 0, 50

        while True:
            batch = self._fetch(offset, batch_size)
            if not batch:
                break

            # normalize each raw listing
            for item in batch:
                listings.append(self._normalize(item))

            if len(batch) < batch_size:
                break
            offset += batch_size

        print(f"✅ Total listings fetched: {len(listings)}")
        return listings

