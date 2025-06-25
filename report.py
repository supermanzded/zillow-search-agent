import os
import pandas as pd


def _flatten_listing(item: dict) -> dict:
    """Convert one raw listing dict from the API into a flat row."""
    addr     = item.get("location", {}).get("address", {})
    descr    = item.get("description", {})

    return {
        "Price":         item.get("list_price"),
        "Beds":          descr.get("beds"),
        "Baths":         descr.get("baths"),
        "Address":       addr.get("line"),
        "City":          addr.get("city"),
        "State":         addr.get("state_code"),
        "ZIP":           addr.get("postal_code"),
        "Property Type": descr.get("type") or item.get("prop_type"),
        "URL":           item.get("href"),
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
