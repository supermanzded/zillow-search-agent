import pandas as pd
import os

def generate_excel_report(data):
    if not data:
        print("⚠️  No data to write. Excel file will not be generated.")
        return None

    df = pd.DataFrame(data)

    # Optional: ensure consistent column order if keys vary
    expected_columns = ["address", "price", "beds", "baths", "url"]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""  # Add missing columns with empty values
    df = df[expected_columns]  # Reorder

    filepath = "zillow_report.xlsx"
    df.to_excel(filepath, index=False)
    print(f"✅ Excel report saved to: {filepath}")
    return filepath
