"""
Test Chatbot API Endpoints with Authentication
"""
import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
CHAT_URL = f"{BASE_URL}/api/chatbot/chatbot/chat/"
STREAM_CHAT_URL = f"{BASE_URL}/api/chatbot/chatbot/stream_chat/"
HISTORY_URL = f"{BASE_URL}/api/chatbot/chatbot/history/"
QUICK_QUERY_URL = f"{BASE_URL}/api/chatbot/chatbot/quick_query/"

# Test credentials
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"  # Default Django admin password
}

# Global session for authentication
session = requests.Session()

def login() -> bool:
    """Login and get authentication token"""
    print("🔐 Logging in...")

    try:
        response = session.post(LOGIN_URL, json=TEST_CREDENTIALS)

        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                session.headers.update({
                    'Authorization': f"Token {data['token']}"
                })
                print("✅ Login successful")
                return True
            else:
                print("❌ No token in response")
                print(f"Response: {data}")
                return False
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def test_chat_endpoint():
    """Test the main chat endpoint"""
    print("\n💬 Testing Chat Endpoint...")

    test_messages = [
        "ما هو نظام مستشفى المنصورة؟",
        "What is an antibiogram?",
        "كيف أضيف مريض جديد؟",
        "How do I read a heat map?"
    ]

    for message in test_messages:
        print(f"\n📤 Sending: '{message}'")

        try:
            response = session.post(CHAT_URL, json={"message": message}, timeout=60)

            if response.status_code == 200:
                data = response.json()
                print("✅ Response received:")
                print(f"   Language: {data.get('language', 'unknown')}")
                print(f"   Response: {data.get('response', '')[:200]}...")
                print(f"   Sources: {data.get('sources', [])}")
            else:
                print(f"❌ Chat failed with status: {response.status_code}")
                print(f"   Response: {response.text}")

        except requests.exceptions.Timeout:
            print("⏰ Request timed out (this is normal for first AI request)")
        except Exception as e:
            print(f"❌ Chat error: {str(e)}")

def test_quick_query_endpoint():
    """Test the quick query endpoint"""
    print("\n🔍 Testing Quick Query Endpoint...")

    queries = [
        {"type": "bacteria_count"},
        {"type": "antibiotic_count"},
        {"type": "sample_count"}
    ]

    for query in queries:
        print(f"\n📤 Query: {query}")

        try:
            response = session.post(QUICK_QUERY_URL, json=query, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print("✅ Query result:")
                print(f"   {data}")
            else:
                print(f"❌ Query failed with status: {response.status_code}")
                print(f"   Response: {response.text}")

        except Exception as e:
            print(f"❌ Query error: {str(e)}")

def test_history_endpoint():
    """Test the chat history endpoint"""
    print("\n📚 Testing History Endpoint...")

    try:
        response = session.get(HISTORY_URL, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print("✅ History retrieved:")
            print(f"   {len(data)} messages found")
            if data:
                print(f"   Latest message: {data[0].get('message', '')[:50]}...")
        else:
            print(f"❌ History failed with status: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ History error: {str(e)}")

def test_stream_chat_endpoint():
    """Test the streaming chat endpoint"""
    print("\n🌊 Testing Stream Chat Endpoint...")

    message = "What is MIC?"
    print(f"\n📤 Streaming: '{message}'")

    try:
        response = session.post(STREAM_CHAT_URL, json={"message": message}, stream=True, timeout=60)

        if response.status_code == 200:
            print("✅ Stream started...")
            chunks_received = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: '
                            if 'chunk' in data:
                                chunks_received += 1
                                if chunks_received <= 3:  # Show first 3 chunks
                                    print(f"   📦 Chunk {chunks_received}: {data['chunk'][:50]}...")
                            elif 'done' in data:
                                print(f"✅ Stream completed with {chunks_received} chunks")
                                break
                            elif 'error' in data:
                                print(f"❌ Stream error: {data['error']}")
                                break
                        except json.JSONDecodeError:
                            continue

            if chunks_received == 0:
                print("⚠️  No chunks received")
        else:
            print(f"❌ Stream failed with status: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.Timeout:
        print("⏰ Stream request timed out")
    except Exception as e:
        print(f"❌ Stream error: {str(e)}")

def main():
    """Run all API tests"""
    print("🤖 CHATBOT API TESTING SUITE")
    print("=" * 50)

    # Login first
    if not login():
        print("❌ Cannot proceed without authentication")
        return

    # Test endpoints
    test_chat_endpoint()
    test_quick_query_endpoint()
    test_history_endpoint()
    test_stream_chat_endpoint()

    print("\n" + "=" * 50)
    print("🎉 API TESTING COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    main()
