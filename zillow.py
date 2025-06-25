import os
import requests


class ZillowClient:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://realtor-search.p.rapidapi.com/properties/nearby-home-values?lat=40.23184&lon=-76.895774"
        self.headers = {
            "x-rapidapi-host: realtor-search.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }
        self.lat = 27.4956  # Sebring, FL
        self.lon = -81.4409
        print("ZillowClient (Realtor Search API) initialized.")

    def search_properties(self):
        print("Starting property search...")
        listings = []
        offset = 0
        limit = 200

        while True:
            print(f"Fetching batch starting at offset {offset}...")
            batch = self._query_batch(offset, limit)

            if not batch:
                break

            listings.extend(batch)
            if len(batch) < limit:
                break
            offset += limit

        print(f"✅ Retrieved {len(listings)} listings.")
        return listings

    def _query_batch(self, offset, limit):
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "radius": 105,
            "limit": limit,
            "offset": offset,
            "beds_min": 2,
            "baths_min": 1,
            "price_min": 200000,
            "price_max": 400000,
            "property_type": "multi_family",
            "sort": "newest"
        }

        response = requests.get(self.base_url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        props = data.get("data", {}).get("home_search", {}).get("results", [])

        parsed = []
        for p in props:
            parsed.append({
                "address": p.get("location", {}).get("address", {}).get("line", "N/A"),
                "price": p.get("list_price", "N/A"),
                "beds": p.get("description", {}).get("beds", "N/A"),
                "baths": p.get("description", {}).get("baths", "N/A"),
                "units": "N/A"  # May not be available in this endpoint
            })

        print(f"🔹 Found {len(parsed)} listings in this batch.")
        return parsed
