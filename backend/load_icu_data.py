import pandas as pd
from antibiogram.settings import BASE_DIR
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from users.models import User
from django.core.management.base import BaseCommand
import re
from datetime import datetime

class Command(BaseCommand):
    help = 'Load ICU antibiotic data from Excel file'

    def handle(self, *args, **options):
        # Load Excel file
        file_path = BASE_DIR / 'DB' / 'ICU antibiotic.xlsx'

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
        admin_user = User.objects.get(username='admin')

        # Process sensitivity data
        self.stdout.write('Processing sensitivity data...')

        for idx, row in sensitivity_df.iterrows():
            try:
                # Create or get bacteria
                bacteria_name = row['strain'].strip() if pd.notna(row['strain']) else f"Unknown_{row['code']}"
                bacteria, created = Bacteria.objects.get_or_create(
                    name=bacteria_name,
                    defaults={
                        'bacteria_type': 'gram_negative',  # Most ICU pathogens are gram-negative
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
                            # Clean and map sensitivity value
                            clean_value = str(sensitivity_value).strip()
                            mapped_sensitivity = sensitivity_mapping.get(clean_value, 'Not Done')

                            # Skip 'Not Done' results
                            if mapped_sensitivity != 'Not Done':
                                # Create or get antibiotic
                                antibiotic, created = Antibiotic.objects.get_or_create(
                                    name=col,
                                    defaults={
                                        'category': 'Unknown',  # Will be updated if more info available
                                        'mechanism': 'Unknown',
                                        'common_use': 'ICU infections',
                                        'notes': 'ICU antibiotic data'
                                    }
                                )

                                # Create test result
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
                self.stdout.write(self.style.WARNING(f'Error processing row {idx}: {e}'))
                continue

        # Process MIC data
        self.stdout.write('Processing MIC data...')

        for idx, row in mic_df.iterrows():
            try:
                # Find corresponding sample
                bacteria_name = row['strain'].strip() if pd.notna(row['strain']) else f"Unknown_{row['code']}"
                try:
                    bacteria = Bacteria.objects.get(name=bacteria_name)
                    sample = Sample.objects.get(
                        patient_id=f'ICU_{row["code"]}',
                        bacteria=bacteria
                    )
                except (Bacteria.DoesNotExist, Sample.DoesNotExist):
                    continue

                # Process each antibiotic MIC value
                for col in mic_df.columns:
                    if col not in ['code', 'strain']:
                        mic_value = row[col]
                        if pd.notna(mic_value):
                            # Parse MIC value (e.g., ">=32", "<=1", "=4/76")
                            mic_str = str(mic_value).strip()

                            # Create or get antibiotic
                            antibiotic, created = Antibiotic.objects.get_or_create(
                                name=col,
                                defaults={
                                    'category': 'Unknown',
                                    'mechanism': 'Unknown',
                                    'common_use': 'ICU infections',
                                    'notes': 'ICU antibiotic data with MIC'
                                }
                            )

                            # Update existing test result with MIC value
                            try:
                                test_result = TestResult.objects.get(
                                    sample=sample,
                                    antibiotic=antibiotic
                                )
                                test_result.mic_value = mic_str
                                test_result.save()
                            except TestResult.DoesNotExist:
                                # Create new result if doesn't exist
                                TestResult.objects.create(
                                    sample=sample,
                                    antibiotic=antibiotic,
                                    sensitivity='unknown',  # Will be determined from sensitivity sheet
                                    zone_diameter=None,
                                    mic_value=mic_str,
                                    notes=f'ICU MIC data - Code: {row["code"]}'
                                )

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error processing MIC row {idx}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS('Successfully loaded ICU antibiotic data'))

        # Print summary
        total_bacteria = Bacteria.objects.filter(notes__contains='ICU isolate').count()
        total_samples = Sample.objects.filter(department='ICU').count()
        total_results = TestResult.objects.filter(notes__contains='ICU data').count()

        self.stdout.write(f'Loaded {total_bacteria} ICU bacteria strains')
        self.stdout.write(f'Created {total_samples} ICU samples')
        self.stdout.write(f'Generated {total_results} test results')
