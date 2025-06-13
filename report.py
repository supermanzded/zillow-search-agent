import pandas as pd

def generate_excel_report(data):
    df = pd.DataFrame(data)
    filepath = "/mnt/data/zillow_report.xlsx"
    df.to_excel(filepath, index=False)
    return filepath
