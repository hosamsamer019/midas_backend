#!/usr/bin/env python
"""
Analyze ICU antibiotic data loaded from Excel
"""
import os
import sys
import django
import pandas as pd
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from samples.models import Sample
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from results.models import TestResult

def analyze_icu_data():
    print("=== ICU Antibiotic Data Analysis ===\n")

    # Get ICU data
    icu_samples = Sample.objects.filter(department='ICU')
    icu_bacteria = Bacteria.objects.filter(notes__contains='ICU isolate')
    icu_antibiotics = Antibiotic.objects.filter(notes__contains='ICU antibiotic data')
    icu_results = TestResult.objects.filter(notes__contains='ICU data')

    print(f"📊 Data Summary:")
    print(f"   ICU Samples: {icu_samples.count()}")
    print(f"   ICU Bacteria Strains: {icu_bacteria.count()}")
    print(f"   ICU Antibiotics: {icu_antibiotics.count()}")
    print(f"   ICU Test Results: {icu_results.count()}\n")

    if icu_results.exists():
        # Resistance statistics
        print("🏥 Resistance Analysis:")

        # Overall resistance rates
        total_tests = icu_results.count()
        resistant_count = icu_results.filter(sensitivity__iexact='resistant').count()
        sensitive_count = icu_results.filter(sensitivity__iexact='sensitive').count()
        intermediate_count = icu_results.filter(sensitivity__iexact='intermediate').count()

        print(f"   Total Tests: {total_tests}")
        print(f"   Resistant: {resistant_count} ({resistant_count/total_tests*100:.1f}%)")
        print(f"   Sensitive: {sensitive_count} ({sensitive_count/total_tests*100:.1f}%)")
        print(f"   Intermediate: {intermediate_count} ({intermediate_count/total_tests*100:.1f}%)")

        # Top resistant bacteria
        print("\n🦠 Top Resistant Bacteria:")
        bacteria_resistance = defaultdict(lambda: {'total': 0, 'resistant': 0})

        for result in icu_results:
            bacteria_name = result.sample.bacteria.name
            bacteria_resistance[bacteria_name]['total'] += 1
            if result.sensitivity.lower() == 'resistant':
                bacteria_resistance[bacteria_name]['resistant'] += 1

        # Sort by resistance rate
        sorted_bacteria = sorted(
            [(name, stats['resistant']/stats['total']*100, stats['total'])
             for name, stats in bacteria_resistance.items() if stats['total'] > 0],
            key=lambda x: x[1], reverse=True
        )

        for name, rate, total in sorted_bacteria[:10]:
            print(f"   {name}: {rate:.1f}% resistant ({total} tests)")

        # Top antibiotics with resistance
        print("\n💊 Antibiotics with Highest Resistance:")
        antibiotic_resistance = defaultdict(lambda: {'total': 0, 'resistant': 0})

        for result in icu_results:
            antibiotic_name = result.antibiotic.name
            antibiotic_resistance[antibiotic_name]['total'] += 1
            if result.sensitivity.lower() == 'resistant':
                antibiotic_resistance[antibiotic_name]['resistant'] += 1

        # Sort by resistance rate
        sorted_antibiotics = sorted(
            [(name, stats['resistant']/stats['total']*100, stats['total'])
             for name, stats in antibiotic_resistance.items() if stats['total'] > 0],
            key=lambda x: x[1], reverse=True
        )

        for name, rate, total in sorted_antibiotics[:10]:
            print(f"   {name}: {rate:.1f}% resistant ({total} tests)")

        # Most common bacteria
        print("\n🔬 Most Common ICU Bacteria:")
        bacteria_counts = defaultdict(int)
        for sample in icu_samples:
            bacteria_counts[sample.bacteria.name] += 1

        sorted_bacteria_counts = sorted(bacteria_counts.items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_bacteria_counts[:10]:
            print(f"   {name}: {count} isolates")

        print("\n✅ ICU Data Analysis Complete!")
        print("The database has been successfully populated with ICU antibiotic resistance data.")
        print("This data can now be used for antibiogram analysis, resistance trend monitoring,")
        print("and clinical decision support in ICU settings.")

    else:
        print("❌ No ICU test results found in database.")
        print("Please check if the data loading script ran successfully.")

if __name__ == '__main__':
    analyze_icu_data()
