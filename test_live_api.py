import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method} | URL: {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        print(f"Status Code: {response.status_code} (Expected: {expected_status})")
        
        if response.status_code == expected_status:
            print("✅ PASS")
            try:
                json_data = response.json()
                print(f"Response Preview: {json.dumps(json_data, indent=2)[:500]}...")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            print("❌ FAIL")
            print(f"Response: {response.text}")
        
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("="*60)
    print("LIVE API ENDPOINT TESTING")
    print("="*60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test public endpoints
    endpoints = [
        ("Welcome Endpoint", "GET", f"{BASE_URL}/welcome/"),
        ("Stats Endpoint", "GET", f"{BASE_URL}/stats/"),
        ("Bacteria List", "GET", f"{BASE_URL}/bacteria-list/"),
        ("Antibiotics List", "GET", f"{BASE_URL}/antibiotics-list/"),
        ("Departments List", "GET", f"{BASE_URL}/departments-list/"),
        ("Sensitivity Distribution", "GET", f"{BASE_URL}/sensitivity-distribution/"),
        ("Antibiotic Effectiveness", "GET", f"{BASE_URL}/antibiotic-effectiveness/"),
        ("Resistance Over Time", "GET", f"{BASE_URL}/resistance-over-time/"),
        ("Resistance Heatmap", "GET", f"{BASE_URL}/resistance-heatmap/"),
    ]
    
    for name, method, url in endpoints:
        total_tests += 1
        if test_endpoint(name, method, url):
            tests_passed += 1
    
    # Test AI prediction endpoint
    print("\n" + "="*60)
    print("Testing AI Prediction Endpoint")
    print("="*60)
    
    total_tests += 1
    if test_endpoint(
        "AI Predict - E. coli",
        "POST",
        f"{BASE_URL}/ai/predict/",
        data={"bacteria_name": "E. coli"}
    ):
        tests_passed += 1
    
    total_tests += 1
    if test_endpoint(
        "AI Predict - Klebsiella pneumoniae",
        "POST",
        f"{BASE_URL}/ai/predict/",
        data={"bacteria_name": "Klebsiella pneumoniae"}
    ):
        tests_passed += 1
    
    total_tests += 1
    if test_endpoint(
        "AI Predict - Staphylococcus aureus",
        "POST",
        f"{BASE_URL}/ai/predict/",
        data={"bacteria_name": "Staphylococcus aureus"}
    ):
        tests_passed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {total_tests - tests_passed}")
    print(f"Pass Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 All live API tests passed!")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} test(s) failed")

if __name__ == "__main__":
    main()
