import os
import requests
from typing import List, Dict


class ZillowClient:
    """
    Fetch active multi-family *for-sale* listings near Orlando, FL
    using the Realtor Search API (RapidAPI “realtor-search”).
    """

    BASE_URL = "https://realtor-search.p.rapidapi.com/properties/search-buy"
    HOST     = "realtor-search.p.rapidapi.com"

    # ------- search scope -------
    LOCATIONS = [
        "city: Orlando, FL",   # preferred API syntax
        "Orlando, FL",         # fallback plain text
        "32801"                # fallback ZIP code
    ]
    EXPAND_RADIUS = 50   # allowed values: 0, 25, 50 (miles)

    # ------- user filters -------
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
            "X-RapidAPI-Key":  key,
            "X-RapidAPI-Host": self.HOST,
        }
        print("ZillowClient (Realtor Search API) ready.")

    # ---------------------------------------------------------------- helpers
    def _fetch(self, location: str, offset: int = 0, limit: int = 50) -> List[Dict]:
        """Return one page of results (each item is a listing dict)."""
        params = {
            "location":          location,
            "sortBy":            "relevance",
            "expandSearchArea":  str(self.EXPAND_RADIUS),
            "propertyType":      self.PROP_TYPE,
            "prices":            f"{self.PRICE_MIN},{self.PRICE_MAX}",
            "bedrooms":          str(self.BEDS_MIN),
            "bathrooms":         str(self.BATHS_MIN),
            "offset":            str(offset),
            "limit":             str(limit),
        }

        resp = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}", resp.text[:250])
        resp.raise_for_status()

        payload = resp.json()
        data = payload.get("data")
        if not data or "results" not in data:
            print(f"⚠️ No `results` for location='{location}':", payload)
            return []

        return data["results"]

    # ---------------------------------------------------------------- public
    def search_properties(self) -> List[Dict]:
        """Fetch all pages until no more results are returned, with retries on location format."""
        listings: List[Dict] = []

        for loc in self.LOCATIONS:
            print(f"🔍 Trying location: {loc}")
            offset, batch_size = 0, 50
            temp_results: List[Dict] = []

            while True:
                batch = self._fetch(loc, offset, batch_size)
                if not batch:
                    break
                temp_results.extend(batch)
                if len(batch) < batch_size:
                    break  # last page
                offset += batch_size

            if temp_results:
                listings = temp_results
                print(f"✅ Success with location='{loc}', total listings: {len(listings)}")
                break
            else:
                print(f"⚠️ No results with location='{loc}', trying next option...")

        if not listings:
            print("❌ No listings retrieved after trying all location formats.")

        return listings
