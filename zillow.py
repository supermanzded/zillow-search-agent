import os
import requests
import time
from typing import List, Dict

class ZillowClient:
    """
    Fetch listings using the Realtor Search API `search-url` endpoint.
    Includes automatic retries and exponential backoff for rate-limiting.
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

    def search_by_url(self, url: str, retries: int = 3, delay: int = 2) -> List[Dict]:
        """
        Fetch listings from a Realtor.com search URL with automatic retries.
        retries: number of attempts if rate-limited
        delay: initial wait time in seconds, doubles each retry (exponential backoff)
        """
        params = {"url": url}

        for attempt in range(1, retries + 1):
            try:
                resp = requests.get(self.URL_SEARCH, headers=self.headers, params=params, timeout=30)
                if resp.status_code == 200:
                    payload = resp.json()
                    data = payload.get("data")
                    if not data or "results" not in data:
                        print(f"⚠️ No results for URL='{url}':", payload)
                        return []
                    results = data["results"]
                    print(f"✅ URL search successful: {len(results)} listings found")
                    return results

                elif resp.status_code in [429, 400]:
                    print(f"⚠️ Rate limited or bad request. Attempt {attempt}/{retries}. Retrying in {delay} sec...")
                    time.sleep(delay)
                    delay *= 2  # exponential backoff

                else:
                    print(f"❌ HTTP {resp.status_code}: {resp.text[:200]}")
                    resp.raise_for_status()

            except requests.exceptions.RequestException as e:
                print(f"❌ Request exception: {e}. Attempt {attempt}/{retries}. Retrying in {delay} sec...")
                time.sleep(delay)
                delay *= 2

        print("❌ Max retries reached. No results fetched.")
        return []
