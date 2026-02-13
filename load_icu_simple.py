#!/usr/bin/env python
"""
Simple script to load ICU antibiotic data - faster version
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

import pandas as pd
from datetime import datetime
from django.db import transaction

def load_icu_data_simple():
    """Load ICU antibiotic data from Excel file - simplified version"""
    
    # File path
    file_path = os.path.join(os.path.dirname(__file__), 'DB', 'ICU antibiotic.xlsx')
    
    print(f"Loading data from: {file_path}")
    
    # Load Excel file
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1')
        print(f"Loaded {len(df)} rows")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return
    
    # Get models
    from bacteria.models import Bacteria
    from antibiotics.models import Antibiotic
    from samples.models import Sample
    from results.models import TestResult
    
    # Get antibiotic columns
    antibiotic_columns = [col for col in df.columns if col not in ['code', 'strain', 'source']]
    print(f"Antibiotics: {len(antibiotic_columns)}")
    
    # Create antibiotics
    print("Creating antibiotics...")
    for ab_name in antibiotic_columns:
        Antibiotic.objects.get_or_create(
            name=ab_name,
            defaults={
                'category': 'Unknown',
                'mechanism': 'Unknown',
                'common_use': 'ICU infections',
            }
        )
    
    # Get all antibiotics
    antibiotics = {ab.name: ab for ab in Antibiotic.objects.all()}
    print(f"Antibiotics in database: {len(antibiotics)}")
    
    # Process data
    samples_created = 0
    results_created = 0
    results_skipped = 0
    
    sensitivity_map = {
        's': 'sensitive', 'S': 'sensitive',
        'r': 'resistant', 'R': 'resistant', 
        'i': 'intermediate', 'I': 'intermediate',
    }
    
    print("Processing rows...")
    
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                # Get bacteria name
                bacteria_name = row.get('strain')
                if pd.isna(bacteria_name) or str(bacteria_name).strip() == '':
                    results_skipped += 1
                    continue
                
                bacteria_name = str(bacteria_name).strip()
                
                # Get or create bacteria
                bacteria, _ = Bacteria.objects.get_or_create(
                    name=bacteria_name,
                    defaults={
                        'bacteria_type': 'gram_negative',
                        'gram_stain': 'Unknown',
                        'source': str(row.get('source', 'ICU')),
                    }
                )
                
                # Get or create sample
                code = row.get('code')
                patient_id = f'ICU_{code}'
                
                sample, sample_created = Sample.objects.get_or_create(
                    patient_id=patient_id,
                    defaults={
                        'bacteria': bacteria,
                        'hospital': 'ICU Hospital',
                        'department': str(row.get('source', 'ICU')),
                        'date': datetime.now().date(),
                    }
                )
                
                if sample_created:
                    samples_created += 1
                
                # Process antibiotics
                for ab_name in antibiotic_columns:
                    sensitivity_value = row.get(ab_name)
                    
                    if pd.notna(sensitivity_value):
                        clean_value = str(sensitivity_value).strip().lower()
                        mapped_sensitivity = sensitivity_map.get(clean_value)
                        
                        if not mapped_sensitivity:
                            results_skipped += 1
                            continue
                        
                        antibiotic = antibiotics.get(ab_name)
                        if not antibiotic:
                            continue
                        
                        # Create result
                        result, result_created = TestResult.objects.get_or_create(
                            sample=sample,
                            antibiotic=antibiotic,
                            defaults={
                                'sensitivity': mapped_sensitivity,
                            }
                        )
                        
                        if result_created:
                            results_created += 1
                        else:
                            results_skipped += 1
                
            except Exception as e:
                print(f"Error row {idx}: {e}")
                continue
    
    print(f"\n=== SUMMARY ===")
    print(f"Samples created: {samples_created}")
    print(f"Results created: {results_created}")
    print(f"Results skipped: {results_skipped}")
    print(f"\nDatabase counts:")
    print(f"Bacteria: {Bacteria.objects.count()}")
    print(f"Antibiotics: {Antibiotic.objects.count()}")
    print(f"Samples: {Sample.objects.count()}")
    print(f"Test Results: {TestResult.objects.count()}")

if __name__ == '__main__':
    load_icu_data_simple()
