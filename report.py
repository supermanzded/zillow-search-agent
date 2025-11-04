import os
import pandas as pd

def _flatten_listing(item: dict) -> dict:
    """Convert one raw listing dict from the API into a flat row."""
    # The actual data is nested under 'property'
    prop = item.get("property", {})
    addr = prop.get("address", {})
    
    # Get price - it's in listingSubType object
    listing_sub = prop.get("listingSubType", {})
    price = prop.get("price")  # Try direct price first
    if not price:
        price = listing_sub.get("price")  # Or from listingSubType
    
    # Get beds/baths from bedrooms/bathrooms fields
    beds = prop.get("bedrooms")
    baths = prop.get("bathrooms")
    
    # Get property type
    prop_type = prop.get("propertyType") or prop.get("homeType")
    
    # Build URL from zpid
    zpid = prop.get("zpid")
    url = f"https://www.zillow.com/homedetails/{zpid}_zpid/" if zpid else None
    
    return {
        "Price": price,
        "Beds": beds,
        "Baths": baths,
        "Address": addr.get("streetAddress"),
        "City": addr.get("city"),
        "State": addr.get("state"),
        "ZIP": addr.get("zipcode"),
        "Property Type": prop_type,
        "URL": url,
    }

def generate_excel_report(data, filepath: str = "zillow_report.xlsx") -> str | None:
    """Create an Excel file from the raw API listings and return its path."""
    if not data:
        print("⚠️  No data to write. Excel file will not be generated.")
        return None
    
    rows = [_flatten_listing(item) for item in data]
    df = pd.DataFrame(rows)
    
    # ensure consistent order
    column_order = [
        "Price", "Beds", "Baths", "Address", "City",
        "State", "ZIP", "Property Type", "URL",
    ]
    df = df[column_order]
    
    df.to_excel(filepath, index=False)
    print(f"✅ Excel report saved to: {filepath}  ({len(df)} rows)")
    return filepath
