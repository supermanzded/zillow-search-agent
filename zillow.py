import os
import time
import requests


class ZillowClient:
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

    def search_by_url(self, params: dict, retries: int = 3, delay: int = 5):
        """
        Calls Zillow property search via RapidAPI with exponential backoff and detailed error logging.
        Returns a list of property dictionaries.
        """
        if not self.api_key:
            print("❌ No API key found; aborting Zillow search.")
            return []

        for attempt in range(1, retries + 1):
            try:
                resp = requests.get(self.base_url, headers=self.headers, params=params, timeout=20)

                # Handle success
                if resp.status_code == 200:
                    data = resp.json()
                    if "props" in data and data["props"]:
                        return data["props"]
                    else:
                        print("⚠️  Zillow API returned no property data.")
                        return []

                # Handle errors
                else:
                    print(f"⚠️  Attempt {attempt}/{retries} failed - "
                          f"Status: {resp.status_code}, Message: {resp.text[:250]}")

            except Exception as e:
                print(f"❌  Exception on attempt {attempt}: {e}")

            if attempt < retries:
                print(f"⏳  Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2

        print("❌  Max retries reached. No results fetched.")
        return []
