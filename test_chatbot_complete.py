"""
Comprehensive Chatbot Testing Script
Tests all chatbot endpoints and Ollama integration
"""
import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
OLLAMA_URL = "http://localhost:11434"

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_ollama_service():
    """Test if Ollama service is running and has models"""
    print_section("TEST 1: Ollama Service Status")
    
    try:
        # Check if Ollama is running
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✅ Ollama is running")
            print(f"✅ Found {len(models)} model(s):")
            for model in models:
                print(f"   - {model['name']} ({model['size'] / 1e9:.2f} GB)")
            
            test_results["passed"].append("Ollama service is running")
            return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            test_results["failed"].append(f"Ollama status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama service")
        print("   Please ensure Ollama is running: ollama serve")
        test_results["failed"].append("Ollama service not running")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {str(e)}")
        test_results["failed"].append(f"Ollama error: {str(e)}")
        return False


def test_ollama_generation():
    """Test Ollama text generation"""
    print_section("TEST 2: Ollama Text Generation")
    
    try:
        prompt = "What is an antibiogram? Answer in one sentence."
        
        print(f"Sending test prompt: '{prompt}'")
        print("Waiting for response...")
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 100
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '').strip()
            
            if ai_response:
                print(f"✅ Ollama generated response:")
                print(f"   {ai_response[:200]}...")
                test_results["passed"].append("Ollama text generation working")
                return True
            else:
                print("❌ Ollama returned empty response")
                test_results["failed"].append("Empty Ollama response")
                return False
        else:
            print(f"❌ Ollama generation failed with status: {response.status_code}")
            test_results["failed"].append(f"Ollama generation status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama generation: {str(e)}")
        test_results["failed"].append(f"Ollama generation error: {str(e)}")
        return False


def test_django_server():
    """Test if Django server is running"""
    print_section("TEST 3: Django Server Status")
    
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        
        if response.status_code in [200, 404]:  # 404 is ok, means server is running
            print("✅ Django server is running")
            test_results["passed"].append("Django server is running")
            return True
        else:
            print(f"⚠️  Django server returned unexpected status: {response.status_code}")
            test_results["warnings"].append(f"Django status: {response.status_code}")
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        print("   Please ensure Django is running: python manage.py runserver")
        test_results["failed"].append("Django server not running")
        return False
    except Exception as e:
        print(f"❌ Error testing Django: {str(e)}")
        test_results["failed"].append(f"Django error: {str(e)}")
        return False


def test_chatbot_endpoints_structure():
    """Test chatbot endpoint structure (without authentication)"""
    print_section("TEST 4: Chatbot Endpoint Structure")
    
    endpoints = [
        "/api/chatbot/chatbot/",
        "/api/chatbot/chatbot/chat/",
        "/api/chatbot/chatbot/stream_chat/",
        "/api/chatbot/chatbot/history/",
        "/api/chatbot/chatbot/clear_history/",
        "/api/chatbot/chatbot/quick_query/",
        "/api/chatbot/knowledge-base/",
    ]
    
    accessible_count = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            # 401 (Unauthorized) or 405 (Method Not Allowed) means endpoint exists
            if response.status_code in [401, 405, 200]:
                print(f"✅ {endpoint} - Endpoint exists (status: {response.status_code})")
                accessible_count += 1
            elif response.status_code == 404:
                print(f"❌ {endpoint} - Not found")
                test_results["failed"].append(f"Endpoint not found: {endpoint}")
            else:
                print(f"⚠️  {endpoint} - Unexpected status: {response.status_code}")
                test_results["warnings"].append(f"Endpoint {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
            test_results["failed"].append(f"Endpoint error {endpoint}: {str(e)}")
    
    if accessible_count == len(endpoints):
        print(f"\n✅ All {len(endpoints)} endpoints are accessible")
        test_results["passed"].append("All chatbot endpoints exist")
        return True
    else:
        print(f"\n⚠️  {accessible_count}/{len(endpoints)} endpoints are accessible")
        test_results["warnings"].append(f"Only {accessible_count}/{len(endpoints)} endpoints accessible")
        return False


def test_database_models():
    """Test if database models are accessible"""
    print_section("TEST 5: Database Models")
    
    try:
        # Test bacteria endpoint
        response = requests.get(f"{BASE_URL}/api/bacteria-list/", timeout=5)
        
        if response.status_code == 200:
            bacteria = response.json()
            print(f"✅ Bacteria model accessible - {len(bacteria)} records")
            test_results["passed"].append(f"Bacteria model: {len(bacteria)} records")
        else:
            print(f"⚠️  Bacteria endpoint status: {response.status_code}")
            test_results["warnings"].append(f"Bacteria endpoint: {response.status_code}")
        
        # Test antibiotics endpoint
        response = requests.get(f"{BASE_URL}/api/antibiotics/", timeout=5)
        
        if response.status_code == 200:
            antibiotics = response.json()
            print(f"✅ Antibiotic model accessible - {len(antibiotics)} records")
            test_results["passed"].append(f"Antibiotic model: {len(antibiotics)} records")
        else:
            print(f"⚠️  Antibiotic endpoint status: {response.status_code}")
            test_results["warnings"].append(f"Antibiotic endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing database models: {str(e)}")
        test_results["failed"].append(f"Database models error: {str(e)}")
        return False


def test_system_knowledge():
    """Test if system knowledge module works"""
    print_section("TEST 6: System Knowledge Module")
    
    try:
        import sys
        sys.path.insert(0, 'Data_Analysis_Project')
        
        from chatbot.system_knowledge import (
            get_system_knowledge,
            get_bacteria_info,
            get_antibiotic_info,
            get_procedure_info
        )
        
        # Test each function
        system_knowledge = get_system_knowledge()
        if system_knowledge and len(system_knowledge) > 100:
            print(f"✅ get_system_knowledge() - {len(system_knowledge)} characters")
            test_results["passed"].append("System knowledge function works")
        else:
            print("❌ get_system_knowledge() returned insufficient data")
            test_results["failed"].append("System knowledge insufficient")
        
        bacteria_info = get_bacteria_info("E. coli")
        if bacteria_info:
            print(f"✅ get_bacteria_info() - {len(bacteria_info)} characters")
            test_results["passed"].append("Bacteria info function works")
        else:
            print("⚠️  get_bacteria_info() returned no data")
            test_results["warnings"].append("Bacteria info empty")
        
        antibiotic_info = get_antibiotic_info("Vancomycin")
        if antibiotic_info:
            print(f"✅ get_antibiotic_info() - {len(antibiotic_info)} characters")
            test_results["passed"].append("Antibiotic info function works")
        else:
            print("⚠️  get_antibiotic_info() returned no data")
            test_results["warnings"].append("Antibiotic info empty")
        
        procedure_info = get_procedure_info("MIC")
        if procedure_info:
            print(f"✅ get_procedure_info() - {len(procedure_info)} characters")
            test_results["passed"].append("Procedure info function works")
        else:
            print("⚠️  get_procedure_info() returned no data")
            test_results["warnings"].append("Procedure info empty")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import system_knowledge module: {str(e)}")
        test_results["failed"].append(f"System knowledge import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing system knowledge: {str(e)}")
        test_results["failed"].append(f"System knowledge error: {str(e)}")
        return False


def test_utils_localai():
    """Test utils_localai module"""
    print_section("TEST 7: Utils LocalAI Module")
    
    try:
        import sys
        sys.path.insert(0, 'Data_Analysis_Project')
        
        from chatbot.utils_localai import check_ollama_status
        
        status = check_ollama_status()
        
        if status['status'] == 'running':
            print(f"✅ check_ollama_status() - {status['message']}")
            print(f"   Available models: {', '.join(status['available_models'])}")
            test_results["passed"].append("Utils LocalAI module works")
            return True
        else:
            print(f"⚠️  Ollama status: {status['status']}")
            print(f"   Message: {status['message']}")
            test_results["warnings"].append(f"Ollama status: {status['status']}")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import utils_localai module: {str(e)}")
        test_results["failed"].append(f"Utils LocalAI import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing utils_localai: {str(e)}")
        test_results["failed"].append(f"Utils LocalAI error: {str(e)}")
        return False


def print_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["warnings"])
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    
    if test_results["passed"]:
        print("\n✅ PASSED TESTS:")
        for test in test_results["passed"]:
            print(f"   • {test}")
    
    if test_results["failed"]:
        print("\n❌ FAILED TESTS:")
        for test in test_results["failed"]:
            print(f"   • {test}")
    
    if test_results["warnings"]:
        print("\n⚠️  WARNINGS:")
        for test in test_results["warnings"]:
            print(f"   • {test}")
    
    # Overall status
    print("\n" + "=" * 80)
    if len(test_results["failed"]) == 0:
        print("🎉 ALL CRITICAL TESTS PASSED!")
        print("   The chatbot system is ready for use.")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Please review the failed tests above.")
    print("=" * 80 + "\n")


def main():
    """Run all tests"""
    print("\n" + "🤖" * 40)
    print("  COMPREHENSIVE CHATBOT TESTING SUITE")
    print("🤖" * 40)
    
    # Run all tests
    test_ollama_service()
    test_ollama_generation()
    test_django_server()
    test_chatbot_endpoints_structure()
    test_database_models()
    test_system_knowledge()
    test_utils_localai()
    
    # Print summary
    print_summary()
    
    # Save results to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Test results saved to: {filename}")


if __name__ == "__main__":
    main()
