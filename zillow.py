import os
import requests
from typing import List, Dict

class ZillowClient:
    """
    Fetch listings using the Realtor Search API `search-url` endpoint.
    Only URL-based searches are supported on this plan.
    """
    URL_SEARCH = "https://realtor-search.p.rapidapi.com/properties/search-url"
    HOST       = "realtor-search.p.rapidapi.com"

    def __init__(self) -> None:
        key = os.getenv("RAPIDAPI_KEY")
        if not key:
            raise RuntimeError("RAPIDAPI_KEY environment variable not set")

        self.headers = {
            "X-RapidAPI-Key":  key,
            "X-RapidAPI-Host": self.HOST,
        }
        print("ZillowClient (Realtor Search API) ready for URL searches.")

    def search_by_url(self, url: str) -> List[Dict]:
        """Fetch all listings from a Realtor.com search URL."""
        params = {"url": url}

        resp = requests.get(self.URL_SEARCH, headers=self.headers, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code}", resp.text[:250])
            resp.raise_for_status()

        payload = resp.json()
        data = payload.get("data")
        if not data or "results" not in data:
            print(f"⚠️ No `results` for URL='{url}':", payload)
            return []

        results = data["results"]
        print(f"✅ URL search successful: {len(results)} listings found")
        return results
