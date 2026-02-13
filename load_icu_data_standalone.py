#!/usr/bin/env python
"""
Standalone script to load ICU antibiotic data from Excel file
"""

import os
import sys
import django
import pandas as pd
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from users.models import User
from datetime import datetime

def load_icu_data():
    print("Loading ICU antibiotic data from Excel file...")

    # File path
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / 'DB' / 'ICU antibiotic.xlsx'

    if not file_path.exists():
        print(f"❌ Excel file not found: {file_path}")
        return

    print(f"Loading from: {file_path}")

    # Load both sheets
    sensitivity_df = pd.read_excel(file_path, sheet_name='sensitivity')
    mic_df = pd.read_excel(file_path, sheet_name='MIC (µg per ml)')

    # Sensitivity value mapping
    sensitivity_mapping = {
        'S': 'Sensitive',
        'R': 'Resistant',
        'I': 'Intermediate',
        'ND': 'Not Done',
        'D': 'Susceptible',
        'SDD': 'Susceptible Dose Dependent',
        ' ': 'Not Done',
        '  ': 'Not Done',
        'R ': 'Resistant',
        'R  ': 'Resistant',
        'S ': 'Sensitive',
        's': 'Sensitive'
    }

    # Get admin user
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Admin user not found. Please run setup_database.py first.")
        return

    # Process sensitivity data
    print("Processing sensitivity data...")

    for idx, row in sensitivity_df.iterrows():
        try:
            # Create or get bacteria
            bacteria_name = row['strain'].strip() if pd.notna(row['strain']) else f"Unknown_{row['code']}"
            bacteria, created = Bacteria.objects.get_or_create(
                name=bacteria_name,
                defaults={
                    'bacteria_type': 'gram_negative',
                    'gram_stain': 'Negative',
                    'source': row['source'] if pd.notna(row['source']) else 'ICU',
                    'notes': f'ICU isolate - Code: {row["code"]}'
                }
            )

            # Create sample
            sample, created = Sample.objects.get_or_create(
                patient_id=f'ICU_{row["code"]}',
                bacteria=bacteria,
                hospital='ICU Hospital',
                department='ICU',
                date=datetime.now().date(),
                created_by=admin_user
            )

            # Process each antibiotic
            for col in sensitivity_df.columns:
                if col not in ['code', 'strain', 'source']:
                    sensitivity_value = row[col]
                    if pd.notna(sensitivity_value):
                        clean_value = str(sensitivity_value).strip()
                        mapped_sensitivity = sensitivity_mapping.get(clean_value, 'Not Done')

                        if mapped_sensitivity != 'Not Done':
                            antibiotic, created = Antibiotic.objects.get_or_create(
                                name=col,
                                defaults={
                                    'category': 'Unknown',
                                    'mechanism': 'Unknown',
                                    'common_use': 'ICU infections',
                                    'notes': 'ICU antibiotic data'
                                }
                            )

                            TestResult.objects.get_or_create(
                                sample=sample,
                                antibiotic=antibiotic,
                                defaults={
                                    'sensitivity': mapped_sensitivity.lower(),
                                    'zone_diameter': None,
                                    'mic_value': None,
                                    'notes': f'ICU data - Code: {row["code"]}'
                                }
                            )

        except Exception as e:
            print(f'Error processing row {idx}: {e}')
            continue

    # Process MIC data
    print("Processing MIC data...")

    for idx, row in mic_df.iterrows():
        try:
            bacteria_name = row['strain'].strip() if pd.notna(row['strain']) else f"Unknown_{row['code']}"
            try:
                bacteria = Bacteria.objects.get(name=bacteria_name)
                sample = Sample.objects.get(
                    patient_id=f'ICU_{row["code"]}',
                    bacteria=bacteria
                )
            except (Bacteria.DoesNotExist, Sample.DoesNotExist):
                continue

            for col in mic_df.columns:
                if col not in ['code', 'strain']:
                    mic_value = row[col]
                    if pd.notna(mic_value):
                        mic_str = str(mic_value).strip()

                        antibiotic, created = Antibiotic.objects.get_or_create(
                            name=col,
                            defaults={
                                'category': 'Unknown',
                                'mechanism': 'Unknown',
                                'common_use': 'ICU infections',
                                'notes': 'ICU antibiotic data with MIC'
                            }
                        )

                        try:
                            test_result = TestResult.objects.get(
                                sample=sample,
                                antibiotic=antibiotic
                            )
                            test_result.mic_value = mic_str
                            test_result.save()
                        except TestResult.DoesNotExist:
                            TestResult.objects.create(
                                sample=sample,
                                antibiotic=antibiotic,
                                sensitivity='unknown',
                                zone_diameter=None,
                                mic_value=mic_str,
                                notes=f'ICU MIC data - Code: {row["code"]}'
                            )

        except Exception as e:
            print(f'Error processing MIC row {idx}: {e}')
            continue

    print("✅ Successfully loaded ICU antibiotic data")

    # Print summary
    total_bacteria = Bacteria.objects.filter(notes__contains='ICU isolate').count()
    total_samples = Sample.objects.filter(department='ICU').count()
    total_results = TestResult.objects.filter(notes__contains='ICU data').count()

    print(f'Loaded {total_bacteria} ICU bacteria strains')
    print(f'Created {total_samples} ICU samples')
    print(f'Generated {total_results} test results')

if __name__ == '__main__':
    load_icu_data()
