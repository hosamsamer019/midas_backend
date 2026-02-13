#!/usr/bin/env python
"""
Test AI antibiotic prediction functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from ai_engine.train_model import predict_antibiotic
from bacteria.models import Bacteria

def test_ai_prediction():
    """Test AI prediction with available bacteria"""
    print("Testing AI Antibiotic Prediction...")
    print("=" * 50)

    # Get all bacteria from database
    bacteria_list = Bacteria.objects.all()

    if not bacteria_list:
        print("❌ No bacteria found in database. Please add some test data first.")
        return False

    print(f"Found {len(bacteria_list)} bacteria in database:")
    for bacteria in bacteria_list:
        print(f"  - {bacteria.name}")

    print("\nTesting predictions for each bacteria:")
    print("-" * 50)

    success_count = 0
    for bacteria in bacteria_list:
        print(f"\n🧪 Testing {bacteria.name}...")

        try:
            result = predict_antibiotic(bacteria.name)

            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                continue

            print(f"✅ Prediction successful!")
            print(f"   Total antibiotics: {result['total_antibiotics']}")
            print(f"   Tested antibiotics: {result['tested_antibiotics']}")

            if result['recommendations']:
                print("   Top 3 recommendations:")
                for i, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"     {i}. {rec['antibiotic']} - {rec['effectiveness']}% effectiveness ({rec['total_tests']} tests)")
            else:
                print("   No recommendations available (no test data)")

            success_count += 1

        except Exception as e:
            print(f"❌ Prediction failed: {e}")

    print("\n" + "=" * 50)
    print(f"AI Testing Results: {success_count}/{len(bacteria_list)} bacteria tested successfully")

    if success_count > 0:
        print("✅ AI functionality is working!")
        return True
    else:
        print("❌ AI functionality has issues")
        return False

if __name__ == '__main__':
    test_ai_prediction()
