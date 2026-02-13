#!/usr/bin/env python
"""
ICU Antibiotic Data Analysis Script
Tests database connectivity and performs initial analysis on ICU antibiotic data
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
from django.db.models import Count, Q

def test_database_connection():
    """Test database connection and basic functionality"""
    print("🔍 Testing Database Connection...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def analyze_icu_data():
    """Analyze the loaded ICU antibiotic data"""
    print("\n📊 ICU ANTIBIOTIC DATA ANALYSIS")
    print("=" * 50)

    # Basic counts
    icu_samples = Sample.objects.filter(department='ICU')
    icu_bacteria = Bacteria.objects.filter(notes__contains='ICU isolate')
    icu_antibiotics = Antibiotic.objects.filter(notes__contains='ICU antibiotic data')
    icu_results = TestResult.objects.filter(notes__contains='ICU data')

    print(f"ICU Samples: {icu_samples.count()}")
    print(f"ICU Bacteria Strains: {icu_bacteria.count()}")
    print(f"ICU Antibiotics: {icu_antibiotics.count()}")
    print(f"ICU Test Results: {icu_results.count()}")

    if icu_results.count() == 0:
        print("\n❌ No ICU data found in database")
        print("💡 Please run the data loading script first")
        return

    # Resistance analysis
    print("\n🦠 RESISTANCE ANALYSIS")
    print("-" * 30)

    resistance_stats = icu_results.values('sensitivity').annotate(
        count=Count('id')
    ).order_by('-count')

    total_tests = icu_results.count()
    for stat in resistance_stats:
        sensitivity = stat['sensitivity']
        count = stat['count']
        percentage = (count / total_tests) * 100
        print(".1f")

    # Top resistant bacteria
    print("\n🔬 TOP RESISTANT BACTERIA")
    print("-" * 30)

    resistant_results = icu_results.filter(sensitivity__iexact='resistant')
    bacteria_resistance = resistant_results.values(
        'sample__bacteria__name'
    ).annotate(
        total_tests=Count('id'),
        resistant_count=Count('id')
    ).order_by('-resistant_count')[:10]

    for bacteria in bacteria_resistance:
        name = bacteria['sample__bacteria__name']
        resistant = bacteria['resistant_count']
        total = bacteria['total_tests']
        rate = (resistant / total) * 100 if total > 0 else 0
        print(".1f")

    # Most tested antibiotics
    print("\n💊 MOST TESTED ANTIBIOTICS")
    print("-" * 30)

    antibiotic_usage = icu_results.values('antibiotic__name').annotate(
        test_count=Count('id')
    ).order_by('-test_count')[:10]

    for antibiotic in antibiotic_usage:
        name = antibiotic['antibiotic__name']
        count = antibiotic['test_count']
        print(f"{name}: {count} tests")

    # Resistance patterns by antibiotic
    print("\n📈 ANTIBIOTIC RESISTANCE PATTERNS")
    print("-" * 35)

    for antibiotic in antibiotic_usage[:5]:  # Top 5 antibiotics
        name = antibiotic['antibiotic__name']
        abx_results = icu_results.filter(antibiotic__name=name)
        resistant = abx_results.filter(sensitivity__iexact='resistant').count()
        total = abx_results.count()
        if total > 0:
            rate = (resistant / total) * 100
            print(".1f")

    # Department comparison (if we have other departments)
    print("\n🏥 DEPARTMENT COMPARISON")
    print("-" * 25)

    dept_stats = Sample.objects.values('department').annotate(
        sample_count=Count('id')
    ).order_by('-sample_count')

    for dept in dept_stats:
        department = dept['department'] or 'Unknown'
        count = dept['sample_count']
        print(f"{department}: {count} samples")

    print("\n✅ ICU Antibiotic Data Analysis Complete!")
    print("📋 Summary:")
    print(f"   • {icu_bacteria.count()} unique bacterial strains analyzed")
    print(f"   • {icu_antibiotics.count()} antibiotics tested")
    print(f"   • {icu_results.count()} total antibiotic susceptibility tests")
    print(f"   • Data ready for further statistical analysis and reporting")

def main():
    print("🚀 ICU ANTIBIOTIC DATABASE ANALYSIS")
    print("=" * 50)

    # Test database
    if not test_database_connection():
        print("❌ Cannot proceed without database connection")
        return

    # Analyze data
    analyze_icu_data()

    print("\n🎯 ANALYSIS COMPLETE")
    print("The ICU antibiotic database is ready for advanced analysis,")
    print("reporting, and integration with the antibiogram system.")

if __name__ == '__main__':
    main()
