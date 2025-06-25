"""
ZillowClient re-implemented to call the Realtor Data API on RapidAPI.
Keeps the same public method:  search_properties() → List[dict]
"""

import os
import math
from typing import List, Dict

import requests
from dotenv import load_dotenv

# ---------------------------------------------
# Configuration
# ---------------------------------------------
load_dotenv()  # so RAPIDAPI_KEY works locally, too

API_KEY = os.getenv("RAPIDAPI_KEY")
if not API_KEY:
    raise RuntimeError(
        "Missing RAPIDAPI_KEY env var.  "
        "Add it in GitHub Secrets and optionally in a local .env file."
    )

HOST = "realtor.p.rapidapi.com"
BASE_URL = f"https://{HOST}"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": HOST,
    "Accept": "application/json",
}

# Sebring, FL
LAT, LON = 27.4956, -81.4409
RADIUS_MILES = 105

PRICE_MIN, PRICE_MAX = 200_000, 400_000
BEDS_MIN, BATHS_MIN = 2, 1
PROP_TYPE = "multi_family"            # matches Realtor.com terminology
PAGE_SIZE = 200                       # max allowed by the API


class ZillowClient:
    """
    *Not* scraping Zillow any more—name retained so main.py still works.
    """

    def __init__(self):
        print("ZillowClient (via Realtor Data API) initialized.")

    # -----------------------------------------
    # Public: same signature as before
    # -----------------------------------------
    def search_properties(self) -> List[Dict]:
        """Return listings that satisfy all user filters, including central AC."""
        listings: List[Dict] = []
        offset = 0

        while True:
            batch = self._fetch_batch(offset)
            if not batch:
                break

            for item in batch:
                # Secondary filter: make sure each *unit* (if available) is ≥2-bed/1-bath.
                # Realtor API does not expose per-unit beds/baths, so we rely on overall
                # beds_total & baths_total fields—closest proxy to the original spec.
                beds = (item.get("description") or {}).get("beds", 0)
                baths = (item.get("description") or {}).get("baths", 0)
                if beds < BEDS_MIN or baths < BATHS_MIN:
                    continue

                # Fetch detail to verify central AC
                prop_id = item["property_id"]
                if not self._has_central_ac(prop_id):
                    continue

                addr = item["location"]["address"]
                full_address = f'{addr.get("line")}, {addr.get("city")}, {addr.get("state_code")} {addr.get("postal_code")}'
                price_fmt = f'${item["list_price"]:,.0f}'

                listings.append(
                    {
                        "address": full_address,
                        "price": price_fmt,
                        "units": "N/A",  # Realtor API does not expose unit-count
                    }
                )

            # Pagination
            if len(batch) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

        print(f"✅ Found {len(listings)} qualifying properties.")
        return listings

    # -----------------------------------------
    # Internal helpers
    # -----------------------------------------
    def _fetch_batch(self, offset: int):
        """One paginated call to /properties/v3/list"""
        params = {
            "latitude": LAT,
            "longitude": LON,
            "radius": RADIUS_MILES,
            "price_min": PRICE_MIN,
            "price_max": PRICE_MAX,
            "beds_min": BEDS_MIN,
            "baths_min": BATHS_MIN,
            "prop_type": PROP_TYPE,
            "limit": PAGE_SIZE,
            "offset": offset,
            "sort": "newest",
        }
        resp = requests.get(f"{BASE_URL}/properties/v3/list", headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        raw = resp.json()
        return (raw.get("home_search") or {}).get("results", [])

    def _has_central_ac(self, property_id: str) -> bool:
        """Look up one property’s detail and check cooling features."""
        params = {"property_id": property_id}
        resp = requests.get(f"{BASE_URL}/properties/v3/detail", headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        home = (resp.json().get("properties") or [{}])[0]
        # Cooling info can live in several places; normalise to a single string
        cooling_fields = []

        features = home.get("features", {})
        if "cooling" in features:
            cooling_fields += features["cooling"]

        details = home.get("property", {})
        if "cooling" in details:
            cooling_fields += [details["cooling"]]

        combined = " ".join(cooling_fields).lower()
        return "central" in combined  # matches “Central Air”, “Central Cooling”, etc.
