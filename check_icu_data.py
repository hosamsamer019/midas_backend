#!/usr/bin/env python
"""
Check ICU data loaded in database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from samples.models import Sample
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from results.models import TestResult

def check_icu_data():
    print("=== ICU Data Analysis ===")

    # Check ICU samples
    icu_samples = Sample.objects.filter(department='ICU')
    print(f"ICU Samples: {icu_samples.count()}")

    # Check ICU bacteria
    icu_bacteria = Bacteria.objects.filter(notes__contains='ICU isolate')
    print(f"ICU Bacteria: {icu_bacteria.count()}")

    # Check ICU antibiotics
    icu_antibiotics = Antibiotic.objects.filter(notes__contains='ICU antibiotic data')
    print(f"ICU Antibiotics: {icu_antibiotics.count()}")

    # Check ICU test results
    icu_results = TestResult.objects.filter(notes__contains='ICU data')
    print(f"ICU Test Results: {icu_results.count()}")

    # Show some sample data
    if icu_bacteria.exists():
        print("\n=== Sample ICU Bacteria ===")
        for bacteria in icu_bacteria[:5]:
            print(f"- {bacteria.name} ({bacteria.bacteria_type})")

    if icu_antibiotics.exists():
        print("\n=== Sample ICU Antibiotics ===")
        for antibiotic in icu_antibiotics[:5]:
            print(f"- {antibiotic.name}")

    if icu_results.exists():
        print("\n=== Sample ICU Test Results ===")
        for result in icu_results[:5]:
            print(f"- {result.sample.bacteria.name} vs {result.antibiotic.name}: {result.sensitivity}")

    # Basic statistics
    if icu_results.exists():
        print("\n=== ICU Resistance Statistics ===")
        total_results = icu_results.count()
        resistant = icu_results.filter(sensitivity__iexact='resistant').count()
        sensitive = icu_results.filter(sensitivity__iexact='sensitive').count()
        intermediate = icu_results.filter(sensitivity__iexact='intermediate').count()

        print(f"Total test results: {total_results}")
        print(f"Resistant: {resistant} ({resistant/total_results*100:.1f}%)")
        print(f"Sensitive: {sensitive} ({sensitive/total_results*100:.1f}%)")
        print(f"Intermediate: {intermediate} ({intermediate/total_results*100:.1f}%)")

if __name__ == '__main__':
    check_icu_data()
