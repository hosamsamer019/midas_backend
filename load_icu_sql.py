#!/usr/bin/env python
"""
Simple SQL-based data loader - uses raw SQL for speed
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

# Insert antibiotics
print("Inserting antibiotics...")
for ab_name in antibiotic_columns:
    cursor.execute("INSERT OR IGNORE INTO antibiotics_antibiotic (name, category, mechanism, common_use) VALUES (?, ?, ?, ?)",
                   (ab_name, 'Unknown', 'Unknown', 'ICU infections'))

conn.commit()
print(f"Antibiotics inserted")

# Sensitivity mapping
sensitivity_map = {
    's': 'sensitive',
    'S': 'sensitive',
    'r': 'resistant',
    'R': 'resistant',
    'i': 'intermediate',
    'I': 'intermediate',
}

# Insert samples and results
print("Inserting samples and results...")
samples_created = 0
results_created = 0

for idx, row in df.iterrows():
    try:
        # Get bacteria name
        bacteria_name = row.get('strain')
        if pd.isna(bacteria_name) or str(bacteria_name).strip() == '':
            continue
        
        bacteria_name = str(bacteria_name).strip()
        code = row.get('code')
        source = row.get('source')
        
        if pd.isna(source):
            source = 'ICU'
        else:
            source = str(source)
        
        # Insert bacteria
        cursor.execute("INSERT OR IGNORE INTO bacteria_bacteria (name, bacteria_type, gram_stain, source) VALUES (?, ?, ?, ?)",
                       (bacteria_name, 'gram_negative', 'Unknown', source))
        
        # Get bacteria ID
        cursor.execute("SELECT id FROM bacteria_bacteria WHERE name = ?", (bacteria_name,))
        bacteria_result = cursor.fetchone()
        if not bacteria_result:
            continue
        bacteria_id = bacteria_result[0]
        
        # Insert sample
        patient_id = f'ICU_{code}'
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            INSERT OR IGNORE INTO samples_sample 
            (patient_id, bacteria_id, hospital, department, date, created_by_id) 
            VALUES (?, ?, ?, ?, ?, NULL)
        """, (patient_id, bacteria_id, 'ICU Hospital', source, today))
        
        # Get sample ID
        cursor.execute("SELECT id FROM samples_sample WHERE patient_id = ?", (patient_id,))
        sample_result = cursor.fetchone()
        if not sample_result:
            continue
        sample_id = sample_result[0]
        
        if idx == 0:  # Only print first time
            samples_created += 1
        
        # Insert results
        for ab_name in antibiotic_columns:
            sensitivity_value = row.get(ab_name)
            
            if pd.notna(sensitivity_value):
                clean_value = str(sensitivity_value).strip().lower()
                mapped_sensitivity = sensitivity_map.get(clean_value)
                
                if not mapped_sensitivity:
                    continue
                
                # Get antibiotic ID
                cursor.execute("SELECT id FROM antibiotics_antibiotic WHERE name = ?", (ab_name,))
                ab_result = cursor.fetchone()
                if not ab_result:
                    continue
                antibiotic_id = ab_result[0]
                
                # Insert result
                cursor.execute("""
                    INSERT OR IGNORE INTO results_testresult 
                    (sample_id, antibiotic_id, sensitivity, zone_diameter, mic_value) 
                    VALUES (?, ?, ?, NULL, NULL)
                """, (sample_id, antibiotic_id, mapped_sensitivity))
                
                results_created += 1
        
        if idx % 10 == 0:
            conn.commit()
            print(f"Processed {idx + 1} rows...")
            
    except Exception as e:
        print(f"Error row {idx}: {e}")
        continue

conn.commit()
conn.close()

print(f"\n=== SUMMARY ===")
print(f"Samples created: {samples_created}")
print(f"Results created: {results_created}")
print("Done!")
