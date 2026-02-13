#!/usr/bin/env python
"""
Fixed test results loader - properly inserts test results
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'icu_antibiotic.db')

# Excel file path
excel_path = os.path.join(os.path.dirname(__file__), 'DB', 'ICU antibiotic.xlsx')

print(f"Database: {db_path}")
print(f"Excel: {excel_path}")

# Load Excel file
print("Loading Excel file...")
df = pd.read_excel(excel_path, sheet_name='Sheet1')
print(f"Loaded {len(df)} rows")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get antibiotic columns
antibiotic_columns = [col for col in df.columns if col not in ['code', 'strain', 'source']]
print(f"Antibiotic columns: {len(antibiotic_columns)}")

# Sensitivity mapping
sensitivity_map = {
    's': 'sensitive',
    'S': 'sensitive',
    'r': 'resistant',
    'R': 'resistant',
    'i': 'intermediate',
    'I': 'intermediate',
}

# First, verify samples exist
cursor.execute("SELECT COUNT(*) FROM samples_sample")
sample_count = cursor.fetchone()[0]
print(f"Samples in database: {sample_count}")

# Get all antibiotics
cursor.execute("SELECT id, name FROM antibiotics_antibiotic")
antibiotics = cursor.fetchall()
antibiotic_map = {ab[1]: ab[0] for ab in antibiotics}
print(f"Antibiotics in database: {len(antibiotics)}")

# Insert results
print("Inserting test results...")
results_created = 0
skipped = 0

for idx, row in df.iterrows():
    try:
        # Get code
        code = row.get('code')
        if pd.isna(code):
            skipped += 1
            continue
        
        patient_id = f'ICU_{code}'
        
        # Get sample ID
        cursor.execute("SELECT id, bacteria_id FROM samples_sample WHERE patient_id = ?", (patient_id,))
        sample_result = cursor.fetchone()
        
        if not sample_result:
            skipped += 1
            continue
        
        sample_id = sample_result[0]
        
        # Process each antibiotic
        for ab_name in antibiotic_columns:
            sensitivity_value = row.get(ab_name)
            
            if pd.notna(sensitivity_value):
                clean_value = str(sensitivity_value).strip().lower()
                mapped_sensitivity = sensitivity_map.get(clean_value)
                
                if not mapped_sensitivity:
                    continue
                
                antibiotic_id = antibiotic_map.get(ab_name)
                if not antibiotic_id:
                    continue
                
                # Insert result
                try:
                    cursor.execute("""
                        INSERT INTO results_testresult 
                        (sample_id, antibiotic_id, sensitivity, zone_diameter, mic_value, notes) 
                        VALUES (?, ?, ?, NULL, NULL, ?)
                    """, (sample_id, antibiotic_id, mapped_sensitivity, f'ICU data - Code: {code}'))
                    results_created += 1
                except Exception as e:
                    # Try UPDATE if INSERT fails
                    try:
                        cursor.execute("""
                            UPDATE results_testresult 
                            SET sensitivity = ?
                            WHERE sample_id = ? AND antibiotic_id = ?
                        """, (mapped_sensitivity, sample_id, antibiotic_id))
                        if cursor.rowcount > 0:
                            results_created += 1
                    except:
                        pass
        
        if idx % 10 == 0:
            conn.commit()
            print(f"Processed {idx + 1} rows...")
            
    except Exception as e:
        print(f"Error row {idx}: {e}")
        continue

conn.commit()
conn.close()

print(f"\n=== SUMMARY ===")
print(f"Results created: {results_created}")
print(f"Skipped: {skipped}")
print("Done!")

# Verify
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM results_testresult")
count = cursor.fetchone()[0]
print(f"Total results in database: {count}")
conn.close()
