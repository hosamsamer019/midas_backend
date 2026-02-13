#!/usr/bin/env python
"""
Corrected script to load ICU antibiotic data from Excel file
This fixes the issues with the original load_icu_data.py
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
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from users.models import User
from django.db import transaction

def load_icu_data():
    """Load ICU antibiotic data from Excel file"""
    
    # File path
    file_path = os.path.join(os.path.dirname(__file__), 'DB', 'ICU antibiotic.xlsx')
    
    print(f"Loading data from: {file_path}")
    
    # Load Excel file - Sheet1 (not 'sensitivity')
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1')
        print(f"Loaded sheet 'Sheet1' with {len(df)} rows and {len(df.columns)} columns")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return
    
    # Print column names
    print(f"Columns: {list(df.columns[:5])} ... (total {len(df.columns)})")
    
    # Get admin user (or create one if doesn't exist)
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            # Try to get any user
            admin_user = User.objects.first()
        if not admin_user:
            print("Warning: No admin user found, using None")
            admin_user = None
    except Exception as e:
        print(f"Error getting admin user: {e}")
        admin_user = None
    
    # Sensitivity mapping - fix the values
    sensitivity_mapping = {
        's': 'sensitive',
        'S': 'sensitive',
        'r': 'resistant',
        'R': 'resistant',
        'i': 'intermediate',
        'I': 'intermediate',
        'nd': 'not_done',
        'ND': 'not_done',
        'nd ': 'not_done',
    }
    
    # Get antibiotic columns (exclude code, strain, source)
    antibiotic_columns = [col for col in df.columns if col not in ['code', 'strain', 'source']]
    print(f"Antibiotic columns: {len(antibiotic_columns)}")
    
    # Track statistics
    stats = {
        'bacteria_created': 0,
        'bacteria_found': 0,
        'samples_created': 0,
        'antibiotics_created': 0,
        'antibiotics_found': 0,
        'results_created': 0,
        'results_skipped': 0,
    }
    
    # Create antibiotics in bulk first
    print("\n=== Creating antibiotics ===")
    for ab_name in antibiotic_columns:
        ab, created = Antibiotic.objects.get_or_create(
            name=ab_name,
            defaults={
                'category': 'Unknown',
                'mechanism': 'Unknown',
                'common_use': 'ICU infections',
                'notes': 'Loaded from ICU antibiotic data'
            }
        )
        if created:
            stats['antibiotics_created'] += 1
        else:
            stats['antibiotics_found'] += 1
    
    print(f"Antibiotics: {stats['antibiotics_created']} created, {stats['antibiotics_found']} found")
    
    # Process each row
    print("\n=== Processing samples ===")
    
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                # Get bacteria name
                bacteria_name = row['strain']
                if pd.isna(bacteria_name) or str(bacteria_name).strip() == '':
                    # Skip rows without bacteria name
                    print(f"Row {idx}: Skipping - no bacteria name")
                    stats['results_skipped'] += 1
                    continue
                
                bacteria_name = str(bacteria_name).strip()
                
                # Create or get bacteria
                bacteria, created = Bacteria.objects.get_or_create(
                    name=bacteria_name,
                    defaults={
                        'bacteria_type': 'gram_negative',
                        'gram_stain': 'Unknown',
                        'source': str(row['source']) if pd.notna(row['source']) else 'ICU',
                        'notes': f'ICU isolate - Code: {row["code"]}'
                    }
                )
                
                if created:
                    stats['bacteria_created'] += 1
                else:
                    stats['bacteria_found'] += 1
                
                # Get code
                code = row['code']
                patient_id = f'ICU_{code}'
                
                # Create or get sample
                sample, sample_created = Sample.objects.get_or_create(
                    patient_id=patient_id,
                    defaults={
                        'bacteria': bacteria,
                        'hospital': 'ICU Hospital',
                        'department': str(row['source']) if pd.notna(row['source']) else 'ICU',
                        'date': datetime.now().date(),
                        'created_by': admin_user
                    }
                )
                
                if sample_created:
                    stats['samples_created'] += 1
                
                # Process each antibiotic
                for ab_name in antibiotic_columns:
                    sensitivity_value = row[ab_name]
                    
                    if pd.notna(sensitivity_value):
                        # Clean and map sensitivity value
                        clean_value = str(sensitivity_value).strip().lower()
                        mapped_sensitivity = sensitivity_mapping.get(clean_value, 'not_done')
                        
                        # Skip 'not_done' results
                        if mapped_sensitivity == 'not_done':
                            stats['results_skipped'] += 1
                            continue
                        
                        # Get antibiotic
                        try:
                            antibiotic = Antibiotic.objects.get(name=ab_name)
                        except Antibiotic.DoesNotExist:
                            continue
                        
                        # Create test result
                        result, result_created = TestResult.objects.get_or_create(
                            sample=sample,
                            antibiotic=antibiotic,
                            defaults={
                                'sensitivity': mapped_sensitivity,
                                'zone_diameter': None,
                                'mic_value': None,
                                'notes': f'ICU data - Code: {code}'
                            }
                        )
                        
                        if result_created:
                            stats['results_created'] += 1
                        else:
                            stats['results_skipped'] += 1
                
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
    
    # Print summary
    print("\n=== LOADING SUMMARY ===")
    print(f"Bacteria created: {stats['bacteria_created']}")
    print(f"Bacteria found: {stats['bacteria_found']}")
    print(f"Samples created: {stats['samples_created']}")
    print(f"Antibiotics created: {stats['antibiotics_created']}")
    print(f"Antibiotics found: {stats['antibiotics_found']}")
    print(f"Results created: {stats['results_created']}")
    print(f"Results skipped (not done): {stats['results_skipped']}")
    
    # Print current database counts
    print("\n=== CURRENT DATABASE COUNTS ===")
    print(f"Bacteria: {Bacteria.objects.count()}")
    print(f"Antibiotics: {Antibiotic.objects.count()}")
    print(f"Samples: {Sample.objects.count()}")
    print(f"Test Results: {TestResult.objects.count()}")
    
    return stats

if __name__ == '__main__':
    load_icu_data()
