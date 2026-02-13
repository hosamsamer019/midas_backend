import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = 'http://127.0.0.1:8000'
API_URL = f'{BASE_URL}/api'

# Authentication credentials
USERNAME = 'admin'  # Change this to your actual username
PASSWORD = 'admin123'  # Change this to your actual password

# Note: If authentication fails, you may need to create a user first:
# python manage.py createsuperuser --username admin --email admin@example.com

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            f'{API_URL}/auth/token/',
            json={'username': USERNAME, 'password': PASSWORD},
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

# Global auth token
AUTH_TOKEN = None

# Test data
TEST_QUESTIONS = [
    # Medical questions in Arabic
    "ما هو علاج الالتهاب الرئوي البكتيري؟",
    "كيف يمكنني إضافة مريض جديد في النظام؟",
    "ما هي المضادات الحيوية الفعالة ضد البكتيريا المقاومة؟",
    "أريد رؤية نتائج المختبر للمريض رقم 12345",

    # PHI containing questions
    "ما هي نتائج المريض أحمد محمد، رقم الهاتف 0123456789؟",
    "كيف أضيف مريضاً اسمه فاطمة علي، رقم الهوية 123456789؟",

    # System questions
    "كيف أقوم بتصدير التقارير إلى Excel؟",
    "ما هي الخطوات لإنشاء تقرير جديد؟"
]

def test_chat_api():
    """Test the chat API endpoint"""
    print("🧪 Testing Chat API Endpoint...")

    results = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n📝 Test {i}: {question[:50]}...")

        start_time = time.time()

        try:
            response = requests.post(
                f'{API_URL}/chatbot/chatbot/chat/',
                json={'message': question},
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {AUTH_TOKEN}'
                }
            )

            latency = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                sources = data.get('sources', [])
                phi_detected = data.get('phi_detected', False)

                # Check for PHI in response
                phi_in_response = any(phi_word in response_text.lower() for phi_word in [
                    '0123456789', '123456789', 'أحمد محمد', 'فاطمة علي'
                ])

                results.append({
                    'question': question,
                    'response': response_text[:100] + '...' if len(response_text) > 100 else response_text,
                    'sources': sources,
                    'latency': round(latency, 2),
                    'phi_detected': phi_detected,
                    'phi_leaked': phi_in_response,
                    'status': 'PASS'
                })

                print(f"   ✅ Response received ({latency:.2f}s)")
                if phi_detected:
                    print("   🔒 PHI detected and handled")
                if phi_in_response:
                    print("   ⚠️  PHI may have leaked in response")

            else:
                results.append({
                    'question': question,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'status': 'FAIL'
                })
                print(f"   ❌ Error: {response.status_code}")

        except Exception as e:
            results.append({
                'question': question,
                'error': str(e),
                'status': 'ERROR'
            })
            print(f"   💥 Exception: {e}")

    return results

def test_history_api():
    """Test the chat history endpoint"""
    print("\n📚 Testing Chat History API...")

    # Get auth token if not already obtained
    global AUTH_TOKEN
    if not AUTH_TOKEN:
        AUTH_TOKEN = get_auth_token()
        if not AUTH_TOKEN:
            print("❌ Cannot proceed without authentication token")
            return False

    try:
        response = requests.get(
            f'{API_URL}/chatbot/chatbot/history/',
            headers={'Authorization': f'Bearer {AUTH_TOKEN}'}
        )

        if response.status_code == 200:
            history = response.json()
            print(f"   ✅ Retrieved {len(history)} chat messages")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False

def analyze_results(results):
    """Analyze test results"""
    print("\n📊 Test Results Analysis:")

    total_tests = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = total_tests - passed

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    # Check latency
    latencies = [r['latency'] for r in results if 'latency' in r]
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        print(f"Average Latency: {avg_latency:.2f}s")
        print(f"Max Latency: {max_latency:.2f}s")

        # Check latency requirements
        if avg_latency > 1.5:
            print("⚠️  Average latency exceeds 1.5s requirement")
        if max_latency > 3.0:
            print("⚠️  Max latency exceeds 3.0s requirement")

    # Check PHI handling
    phi_tests = [r for r in results if any(phi in r['question'] for phi in ['0123456789', '123456789', 'أحمد محمد', 'فاطمة علي'])]
    phi_leaks = sum(1 for r in phi_tests if r.get('phi_leaked', False))

    if phi_tests:
        print(f"PHI Tests: {len(phi_tests)}")
        print(f"PHI Leaks: {phi_leaks}")
        if phi_leaks > 0:
            print("🚨 PHI leakage detected!")
        else:
            print("🔒 PHI properly anonymized")

    # Check Arabic responses
    arabic_questions = [r for r in results if any(arabic_char in r['question'] for arabic_char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي')]
    arabic_responses = sum(1 for r in arabic_questions if any(arabic_char in r.get('response', '') for arabic_char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'))

    if arabic_questions:
        print(f"Arabic Questions: {len(arabic_questions)}")
        print(f"Arabic Responses: {arabic_responses}")
        if arabic_responses == len(arabic_questions):
            print("🌟 All responses in Arabic")
        else:
            print("⚠️  Some responses not in Arabic")

def save_results(results):
    """Save test results to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'chatbot_test_results_{timestamp}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Results saved to {filename}")

if __name__ == '__main__':
    print("🤖 Smart Antibiogram Chatbot Functionality Test")
    print("=" * 50)

    # Get authentication token first
    AUTH_TOKEN = get_auth_token()
    if not AUTH_TOKEN:
        print("❌ Cannot proceed without authentication token")
        exit(1)

    print(f"✅ Authentication successful")

    # Test chat API
    results = test_chat_api()

    # Test history API
    history_ok = test_history_api()

    # Analyze results
    analyze_results(results)

    # Save results
    save_results(results)

    print("\n🎉 Testing completed!")
    if all(r['status'] == 'PASS' for r in results) and history_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check results above.")
