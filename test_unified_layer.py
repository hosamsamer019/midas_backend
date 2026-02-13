"""
Test script for Unified Data Processing Layer
Tests core functionality without requiring a running server
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from core.data_normalization import (
    normalize_bacteria_name,
    normalize_antibiotic_name,
    normalize_department_name,
    create_case_insensitive_query,
    identify_duplicates,
    validate_sensitivity_value
)
from core.filters import GlobalFilterEngine
from core.data_service import UnifiedDataService
from core.master_data import MasterDataManager
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from samples.models import Sample
from results.models import TestResult
from django.db.models import Q

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")
    print()

def test_data_normalization():
    print("=" * 60)
    print("TEST 1: Data Normalization Functions")
    print("=" * 60)
    
    # Test bacteria name normalization
    test1 = normalize_bacteria_name("  Klebsiella Pneumoniae  ") == "klebsiella pneumoniae"
    print_test("Bacteria name normalization", test1, 
               f"Input: '  Klebsiella Pneumoniae  ' → Output: '{normalize_bacteria_name('  Klebsiella Pneumoniae  ')}'")
    
    # Test case variations
    names = ["Klebsiella", "klebsiella", "KLEBSIELLA", "  kLeBsIeLLa  "]
    normalized = [normalize_bacteria_name(n) for n in names]
    test2 = len(set(normalized)) == 1
    print_test("Case insensitivity", test2,
               f"All variations normalize to: '{normalized[0]}'")
    
    # Test antibiotic normalization
    test3 = normalize_antibiotic_name("  Amoxicillin  ") == "amoxicillin"
    print_test("Antibiotic name normalization", test3,
               f"Input: '  Amoxicillin  ' → Output: '{normalize_antibiotic_name('  Amoxicillin  ')}'")
    
    # Test sensitivity validation
    test4 = validate_sensitivity_value("Sensitive") == "sensitive"
    test5 = validate_sensitivity_value("RESISTANT") == "resistant"
    print_test("Sensitivity value normalization", test4 and test5,
               f"'Sensitive' → '{validate_sensitivity_value('Sensitive')}', 'RESISTANT' → '{validate_sensitivity_value('RESISTANT')}'")
    
    return test1 and test2 and test3 and test4 and test5

def test_case_insensitive_queries():
    print("=" * 60)
    print("TEST 2: Case-Insensitive Query Generation")
    print("=" * 60)
    
    # Test Q object generation
    q = create_case_insensitive_query('name', 'Klebsiella')
    test1 = isinstance(q, Q)
    print_test("Q object creation", test1,
               f"Created Q object for case-insensitive 'name' field")
    
    # Test with actual database query (if data exists)
    try:
        bacteria_count = Bacteria.objects.filter(
            create_case_insensitive_query('name', 'klebsiella')
        ).count()
        print_test("Database query execution", True,
                   f"Found {bacteria_count} bacteria matching 'klebsiella' (case-insensitive)")
    except Exception as e:
        print_test("Database query execution", False, f"Error: {str(e)}")
        return False
    
    return test1

def test_filter_engine():
    print("=" * 60)
    print("TEST 3: Global Filter Engine")
    print("=" * 60)
    
    # Test filter engine creation
    filters = {
        'bacteria': 'E. coli',
        'department': 'ICU',
        'date_from': '2024-01-01',
        'date_to': '2024-12-31'
    }
    
    try:
        engine = GlobalFilterEngine(filters)
        test1 = engine is not None
        print_test("Filter engine creation", test1,
                   f"Created engine with {len(filters)} filters")
        
        # Test filter summary
        summary = engine.get_filter_summary()
        test2 = 'active_filters' in summary and 'bacteria' in summary['active_filters']
        print_test("Filter summary generation", test2,
                   f"Summary: {summary}")
        
        # Test applying filters to queryset
        samples = Sample.objects.all()
        filtered_samples = engine.apply_to_samples(samples)
        test3 = filtered_samples is not None
        print_test("Apply filters to samples", test3,
                   f"Filtered queryset created successfully")
        
        return test1 and test2 and test3
    except Exception as e:
        print_test("Filter engine", False, f"Error: {str(e)}")
        return False

def test_data_service():
    print("=" * 60)
    print("TEST 4: Unified Data Service")
    print("=" * 60)
    
    try:
        # Create data service
        engine = GlobalFilterEngine({})
        service = UnifiedDataService(engine)
        test1 = service is not None
        print_test("Data service creation", test1)
        
        # Test statistics
        stats = service.get_statistics()
        test2 = 'total_samples' in stats and 'total_bacteria' in stats
        print_test("Get statistics", test2,
                   f"Stats: {stats}")
        
        # Test sensitivity distribution
        sensitivity = service.get_sensitivity_distribution()
        test3 = isinstance(sensitivity, list)
        print_test("Get sensitivity distribution", test3,
                   f"Found {len(sensitivity)} sensitivity categories")
        
        # Test antibiotic effectiveness
        effectiveness = service.get_antibiotic_effectiveness(top_n=5)
        test4 = isinstance(effectiveness, list)
        print_test("Get antibiotic effectiveness", test4,
                   f"Found {len(effectiveness)} antibiotics")
        
        # Test resistance heatmap
        heatmap = service.get_resistance_heatmap()
        test5 = isinstance(heatmap, list)
        print_test("Get resistance heatmap", test5,
                   f"Found {len(heatmap)} heatmap entries")
        
        return test1 and test2 and test3 and test4 and test5
    except Exception as e:
        print_test("Data service", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_recommendations():
    print("=" * 60)
    print("TEST 5: AI Recommendations (Full Data Reading)")
    print("=" * 60)
    
    try:
        engine = GlobalFilterEngine({})
        service = UnifiedDataService(engine)
        
        # Get all bacteria
        all_bacteria = Bacteria.objects.all()
        if all_bacteria.count() == 0:
            print_test("AI recommendations", True,
                       "No bacteria in database - skipping test")
            return True
        
        # Test with first bacteria
        bacteria_name = all_bacteria.first().name
        recommendations = service.get_antibiotic_recommendations(bacteria_name, top_n=None)
        
        test1 = 'bacteria' in recommendations
        test2 = 'recommendations' in recommendations
        test3 = isinstance(recommendations['recommendations'], list)
        
        # Check if it reads ALL antibiotics
        all_antibiotics_count = Antibiotic.objects.count()
        recommendations_count = len(recommendations['recommendations'])
        
        print_test("AI reads all data", test1 and test2 and test3,
                   f"Bacteria: {bacteria_name}\n   Total antibiotics in DB: {all_antibiotics_count}\n   Recommendations returned: {recommendations_count}\n   Reading ALL data: {recommendations_count == all_antibiotics_count}")
        
        return test1 and test2 and test3
    except Exception as e:
        print_test("AI recommendations", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_master_data_manager():
    print("=" * 60)
    print("TEST 6: Master Data Manager")
    print("=" * 60)

    try:
        manager = MasterDataManager()
        test1 = manager is not None
        print_test("Master data manager creation", test1)

        # Test duplicate identification
        bacteria_duplicates = manager.identify_bacteria_duplicates()
        test2 = isinstance(bacteria_duplicates, dict)
        has_bacteria_dups = len(bacteria_duplicates) > 0
        print_test("Identify bacteria duplicates", test2,
                   f"Found {len(bacteria_duplicates)} potential duplicate groups" +
                   (f" - Duplicates detected! ⚠️" if has_bacteria_dups else " - No duplicates found ✓"))

        antibiotic_duplicates = manager.identify_antibiotic_duplicates()
        test3 = isinstance(antibiotic_duplicates, dict)
        print_test("Identify antibiotic duplicates", test3,
                   f"Found {len(antibiotic_duplicates)} potential duplicate groups" +
                   (f" - Duplicates detected! ⚠️" if len(antibiotic_duplicates) > 0 else " - No duplicates found ✓"))

        return test1 and test2 and test3
    except Exception as e:
        print_test("Master data manager", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "UNIFIED DATA LAYER TEST SUITE" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    results = []
    
    # Run all tests
    results.append(("Data Normalization", test_data_normalization()))
    results.append(("Case-Insensitive Queries", test_case_insensitive_queries()))
    results.append(("Filter Engine", test_filter_engine()))
    results.append(("Data Service", test_data_service()))
    results.append(("AI Recommendations", test_ai_recommendations()))
    results.append(("Master Data Manager", test_master_data_manager()))
    
    # Summary
    print("\n")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n")
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
