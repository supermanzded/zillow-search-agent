import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "zillow-working-api.p.rapidapi.com")

class ZillowClient:
    def __init__(self):
        if not RAPIDAPI_KEY:
            raise ValueError("RAPIDAPI_KEY not found in .env")
        print("ZillowClient (Working API) initialized and ready.")

    def fetch_listings(self, location="Orlando, FL", max_retries=3):
        url = f"https://{RAPIDAPI_HOST}/custom_ag/byzpid"
        # Example test zpid; real searches would need different endpoints
        params = {"zpid": "44471319"}
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
        }

        for attempt in range(1, max_retries + 1):
            try:
                print(f"Fetching data (attempt {attempt}) from {RAPIDAPI_HOST} …")
                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    print("✅ Zillow API call successful.")
                    return response.json()

                else:
                    print(f"⚠️  Status {response.status_code}: {response.text}")
                    if response.status_code == 403:
                        print("❌ You may not be subscribed to this endpoint or used the wrong host.")
                    time.sleep(attempt * 5)

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                time.sleep(attempt * 5)

        print("🚫 Max retries reached. No data retrieved.")
        return None


if __name__ == "__main__":
    client = ZillowClient()
    data = client.fetch_listings()

    if data:
        print("Sample data retrieved:")
        print(data)
    else:
        print("No listings returned.")
