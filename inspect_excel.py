#!/usr/bin/env python
"""
Inspect the ICU antibiotic Excel file to understand its structure
"""
import pandas as pd

def inspect_excel():
    file_path = 'DB/ICU antibiotic.xlsx'

    try:
        # Load the Excel file
        xl = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl.sheet_names}")

        # Load the first sheet
        df = pd.read_excel(file_path, sheet_name=xl.sheet_names[0])
        print(f"\nData shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst 10 rows:")
        print(df.head(10))

        # Check for unique values in potential key columns
        print(f"\nUnique values in first few columns:")
        for i, col in enumerate(df.columns[:5]):
            unique_vals = df[col].unique()[:10]  # First 10 unique values
            print(f"{col}: {unique_vals}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    inspect_excel()
