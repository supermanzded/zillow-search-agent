class ZillowClient:
    def search_properties(self):
    results = self.api.search(
        location="Sebring, FL",
        radius=105,
        property_type="multi-family",
        price_min=200000,
        price_max=400000,
        min_beds=2,
        min_baths=1,
        features=["central_air"]
    )
    return results
