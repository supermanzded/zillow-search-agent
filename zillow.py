import os
import requests

class ZillowClient:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        if not self.api_key:
            raise ValueError("RAPIDAPI_KEY environment variable not set")
        
        self.base_url = "https://realtor-search.p.rapidapi.com/properties/list-for-sale"
        self.headers = {
            "x-rapidapi-host": "realtor-search.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }
        self.lat = 27.4956  # Sebring, FL latitude
        self.lon = -81.4409  # Sebring, FL longitude
        print("ZillowClient (Realtor Search API) initialized.")

    def _query_batch(self, offset=0, limit=50):
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "radius": 105,  # miles
            "limit": limit,
            "offset": offset,
            "beds_min": 2,
            "baths_min": 1,
            "price_min": 200000,
            "price_max": 400000,
            "property_type": "multi_family",
            "sort": "newest"
        }
        print(f"Fetching batch starting at offset {offset}...")
        response = requests.get(self.base_url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("properties", [])

    def search_properties(self):
        print("Starting property search...")
        listings = []
        offset = 0
        limit = 50
        while True:
            batch = self._query_batch(offset=offset, limit=limit)
            if not batch:
                break
            listings.extend(batch)
            if len(batch) < limit:
                break
            offset += limit
        print(f"Retrieved {len(listings)} listings.")
        return listings
