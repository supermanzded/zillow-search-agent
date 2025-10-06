import os
import time
import requests


class ZillowClient:
    """
    ZillowClient connects to the Zillow RapidAPI endpoint.
    Provides robust logging, error handling, and exponential backoff.
    """

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.base_url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
        self.headers = {
            "x-rapidapi-host": "zillow-com1.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }

        if not self.api_key:
            print("❌ RAPIDAPI_KEY missing from environment variables.")
        else:
            print("ZillowClient (Realtor Search API) ready for URL searches.")

    # ─────────────────────────────────────────── Zillow API Call
    def search_by_url(self, params: dict, retries: int = 3, delay: int = 5):
        """
        Calls Zillow property search via RapidAPI with exponential backoff and detailed error logging.
        Returns a list of property dictionaries if successful.
        """
        if not self.api_key:
            print("❌ No API key found; aborting Zillow search.")
            return []

        url = self.base_url
        print(f"🔍 Querying Zillow API: {url}")
        print(f"🔧 Parameters: {params}")

        for attempt in range(1, retries + 1):
            try:
                resp = requests.get(url, headers=self.headers, params=params, timeout=20)

                print(f"🔹 HTTP {resp.status_code}")
                if resp.status_code != 200:
                    # Show partial response for easier debugging
                    print(f"🔸 Response text: {resp.text[:500]}")

                # ─────────────────────────── Successful response
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except Exception as e:
                        print(f"❌ Failed to parse JSON: {e}")
                        print(f"Raw text: {resp.text[:500]}")
                        return []

                    if "props" in data and isinstance(data["props"], list):
                        print(f"✅ Zillow returned {len(data['props'])} properties.")
                        return data["props"]

                    # If response shape changed
                    print(f"⚠️  Unexpected JSON keys: {list(data.keys())}")
                    if "message" in data:
                        print(f"⚠️  Message from API: {data['message']}")
                    return []

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error on attempt {attempt}: {e}")

            # ─────────────────────────── Retry handling
            if attempt < retries:
                print(f"⏳ Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # exponential backoff

        print("❌ Max retries reached. No results fetched.")
        return []


# ─────────────────────────────────────────── Manual test
if __name__ == "__main__":
    """
    Run this file directly to test your RapidAPI connection without main.py.
    """
    from dotenv import load_dotenv
    load_dotenv()

    client = ZillowClient()

    payload = {
        "location": "Orlando, FL",
        "status_type": "ForSale",
        "page": 1
    }

    results = client.search_by_url(payload, retries=2, delay=5)
    print(f"\n🔎 Test complete. Results fetched: {len(results)}")
