#!/usr/bin/env python
"""
Test script to verify that the 500 errors in API endpoints have been fixed.
This tests the critical endpoints that were previously failing.
"""

import requests
import json
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
import django
django.setup()

# Base URL for the API (assuming local development server)
BASE_URL = 'http://localhost:8000/api'

def test_endpoint(endpoint, method='GET', data=None, description=""):
    """Test a single endpoint and return the result."""
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTesting {method} {endpoint} - {description}")

    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"  ❌ Unsupported method: {method}")
            return False

        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  ✅ SUCCESS: Endpoint returned 200 OK")
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"  📊 Returned {len(data)} items")
                elif isinstance(data, dict):
                    print(f"  📊 Returned data with {len(data)} keys")
                return True
            except:
                print("  📄 Returned non-JSON response")
                return True
        elif response.status_code == 500:
            print("  ❌ FAILED: Still returning 500 Internal Server Error")
            try:
                error_data = response.json()
                print(f"  Error details: {error_data}")
            except:
                print(f"  Raw response: {response.text[:200]}...")
            return False
        else:
            print(f"  ⚠️  WARNING: Unexpected status code {response.status_code}")
            try:
                data = response.json()
                print(f"  Response: {data}")
            except:
                print(f"  Raw response: {response.text[:200]}...")
            return True  # Not a 500 error, so consider it fixed

    except requests.exceptions.ConnectionError:
        print("  ❌ FAILED: Could not connect to server. Is Django running?")
        print("  Please start the Django server with: python manage.py runserver")
        return False
    except requests.exceptions.Timeout:
        print("  ❌ FAILED: Request timed out")
        return False
    except Exception as e:
        print(f"  ❌ FAILED: Exception occurred: {str(e)}")
        return False

def main():
    """Run all the critical endpoint tests."""
    print("=" * 60)
    print("TESTING API ENDPOINTS FOR 500 ERROR FIXES")
    print("=" * 60)

    # List of endpoints to test
    endpoints_to_test = [
        ('/stats/', 'GET', None, 'Dashboard statistics'),
        ('/bacteria-list/', 'GET', None, 'Bacteria list for dropdowns'),
        ('/resistance-heatmap/', 'GET', None, 'Resistance heatmap data'),
        ('/sensitivity-distribution/', 'GET', None, 'Sensitivity distribution chart'),
        ('/antibiotic-effectiveness/', 'GET', None, 'Antibiotic effectiveness data'),
        ('/resistance-over-time/', 'GET', None, 'Resistance over time trends'),
        ('/antibiotics-list/', 'GET', None, 'Antibiotics list for dropdowns'),
        ('/departments-list/', 'GET', None, 'Departments list for filters'),
        ('/ai/predict/', 'POST', {'bacteria_name': 'E. coli'}, 'AI antibiotic predictions'),
    ]

    results = []

    for endpoint, method, data, description in endpoints_to_test:
        success = test_endpoint(endpoint, method, data, description)
        results.append((endpoint, success))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    successful = sum(1 for _, success in results if success)
    total = len(results)

    for endpoint, success in results:
        status = "✅ FIXED" if success else "❌ STILL BROKEN"
        print(f"{endpoint:<25} {status}")

    print(f"\nOverall: {successful}/{total} endpoints working")

    if successful == total:
        print("🎉 ALL ENDPOINTS SUCCESSFULLY FIXED!")
        return 0
    else:
        print("⚠️  Some endpoints still have issues. Check the logs above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
