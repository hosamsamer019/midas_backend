import pandas as pd
from antibiogram.settings import BASE_DIR
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from users.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Load initial data from Excel file'

    def handle(self, *args, **options):
        # Load Excel file
        file_path = BASE_DIR / 'DB' / 'Antibiogram_Test_Dataset.xlsx'
        bacteria_df = pd.read_excel(file_path, sheet_name='Bacteria_Data')
        antibiotics_df = pd.read_excel(file_path, sheet_name='Antibiotics_Data')
        results_df = pd.read_excel(file_path, sheet_name='Test_Results')

        # Load bacteria
        for _, row in bacteria_df.iterrows():
            Bacteria.objects.get_or_create(
                name=row['Bacteria_Name'],
                defaults={
                    'bacteria_type': row['Bacteria_Type'].lower().replace(' ', '_'),
                    'gram_stain': row['Gram_Stain'],
                    'source': row['Source'],
                    'notes': row.get('Notes', '')
                }
            )

        # Load antibiotics
        for _, row in antibiotics_df.iterrows():
            Antibiotic.objects.get_or_create(
                name=row['Antibiotic_Name'],
                defaults={
                    'category': row['Category'],
                    'mechanism': row['Mechanism'],
                    'common_use': row['Common_Use'],
                    'notes': row.get('Notes', '')
                }
            )

        # Get admin user
        admin_user = User.objects.get(username='admin')

        # Load samples and results
        for _, row in results_df.iterrows():
            bacteria = Bacteria.objects.get(name=row['Bacteria_Name'])
            antibiotic = Antibiotic.objects.get(name=row['Antibiotic_Name'])

            sample, created = Sample.objects.get_or_create(
                patient_id=row['Patient_ID'],
                bacteria=bacteria,
                hospital='Test Hospital',
                department=row['Hospital_Department'],
                date=row['Date'],
                created_by=admin_user
            )

            TestResult.objects.get_or_create(
                sample=sample,
                antibiotic=antibiotic,
                defaults={
                    'sensitivity': row['Result'].lower(),
                    'zone_diameter': row.get('Zone_mm', None),
                    'notes': ''
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
