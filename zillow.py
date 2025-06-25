"""
zillow.py  – now powered by the Realtor16 REST API
--------------------------------------------------
• Pulls properties *for-sale* within 105 mi of Sebring FL
• Filters price ($200-400 k), ≥ 2 beds, ≥ 1 bath, multi-family
• Verifies “central air” in the detail call
Requires  :  RAPIDAPI_KEY  in repo secrets
Endpoints :  GET /search/forsale/coordinates
             GET /properties/v3/detail         (same host)
"""

import os
from typing import List, Dict

import requests
from dotenv import load_dotenv

# ───────────────────────────────────────────────────────────
# Config & constants
# ───────────────────────────────────────────────────────────
load_dotenv()                       # makes local .env optional
API_KEY = os.getenv("RAPIDAPI_KEY")
if not API_KEY:
    raise RuntimeError("Missing RAPIDAPI_KEY env var or secret.")

HOST = "realtor16.p.rapidapi.com"
BASE = f"https://{HOST}"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": HOST,
    "accept": "application/json",
}

LAT, LON = 27.4956, -81.4409          # Sebring FL
RADIUS = 105                          # miles
PRICE_MIN, PRICE_MAX = 200_000, 400_000
BEDS_MIN, BATHS_MIN = 2, 1
PAGE_SIZE = 200                       # API default is 20; 200 works fine

# property_type values accepted by the endpoint:
#   single_family, condo, townhouse, multi_family, land, farm, apartment …
PROP_TYPE = "multi_family"


class ZillowClient:
    def __init__(self) -> None:
        print("ZillowClient (Realtor16 API) initialized.")

    # ── public ────────────────────────────────────────────
    def search_properties(self) -> List[Dict]:
        listings: List[Dict] = []
        offset = 0

        while True:
            batch = self._query_batch(offset)
            if not batch:
                break

            for item in batch:
                if not self._qualifies_basic(item):
                    continue

                prop_id = item["property_id"]
                if not self._has_central_air(prop_id):
                    continue

                listings.append(self._format_card(item))

            if len(batch) < PAGE_SIZE:
                break
            offset += PAGE_SIZE

        print(f"✅ Found {len(listings)} qualifying properties.")
        return listings

    # ── helpers ───────────────────────────────────────────
    def _query_batch(self, offset: int):
        """
        One call to /search/forsale/coordinates
        Docs: the endpoint accepts   latitude, longitude, radius,
              limit, offset, sort, beds_min, baths_min, price_min, price_max,
              property_type  (comma-separated list)
        """
        params = {
            "latitude": LAT,
            "longitude": LON,
            "radius": RADIUS,
            "limit": PAGE_SIZE,
            "offset": offset,
            "sort": "newest",            # or 'distance' / 'relevance'
            "beds_min": BEDS_MIN,
            "baths_min": BATHS_MIN,
            "price_min": PRICE_MIN,
            "price_max": PRICE_MAX,
            "property_type": PROP_TYPE,
        }
        r = requests.get(f"{BASE}/search/forsale/coordinates",
                         headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("data", {}).get("home_search", {}).get("results", [])

    def _qualifies_basic(self, item: Dict) -> bool:
        """Secondary guard: some edge cases still slip through."""
        desc = item.get("description", {})
        return (
            desc.get("beds", 0) >= BEDS_MIN and
            desc.get("baths", 0) >= BATHS_MIN and
            PRICE_MIN <= item.get("list_price", 0) <= PRICE_MAX
        )

    def _has_central_air(self, prop_id: str) -> bool:
        """Detail call → look for 'central' in cooling features."""
        params = {"property_id": prop_id}
        r = requests.get(f"{BASE}/properties/v3/detail",
                         headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        prop = (r.json().get("data", {}).get("property", [{}]) or [{}])[0]

        features = " ".join(
            (prop.get("features", {}).get("cooling", [])) +
            [prop.get("property", {}).get("cooling", "")]
        ).lower()
        return "central" in features

    @staticmethod
    def _format_card(item: Dict) -> Dict:
        addr = item["location"]["address"]
        return {
            "address": f'{addr.get("line")}, {addr.get("city")}, '
                       f'{addr.get("state_code")} {addr.get("postal_code")}',
            "price": f'${item["list_price"]:,.0f}',
            "units": "N/A",          # Realtor API has no per-unit breakdown
        }
