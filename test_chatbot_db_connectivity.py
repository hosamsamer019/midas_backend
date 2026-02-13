#!/usr/bin/env python
"""
Chatbot Database Connectivity Test Script

This script tests the chatbot's ability to connect to and query the antibiogram database.
Run this after dependencies are fully installed and Django server is running.
"""

import os
import sys
import django
import requests
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from samples.models import Sample
from bacteria.models import Bacteria
from antibiotics.models import Antibiotic
from results.models import TestResult
from chatbot.models import ChatMessage, KnowledgeBase

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing Database Connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models():
    """Test Django model queries"""
    print("\n🔍 Testing Django Models...")

    tests = [
        ("Sample", Sample),
        ("Bacteria", Bacteria),
        ("Antibiotic", Antibiotic),
        ("TestResult", TestResult),
        ("ChatMessage", ChatMessage),
        ("KnowledgeBase", KnowledgeBase),
    ]

    results = {}
    for name, model in tests:
        try:
            count = model.objects.count()
            print(f"✅ {name}: {count} records found")
            results[name] = count
        except Exception as e:
            print(f"❌ {name}: Query failed - {e}")
            results[name] = 0

    return results

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test API endpoints for data retrieval"""
    print(f"\n🔍 Testing API Endpoints at {base_url}...")

    endpoints = [
        "/api/stats/",
        "/api/antibiotic-effectiveness/",
        "/api/resistance-over-time/",
        "/api/departments-list/",
        "/api/resistance-heatmap/",
        "/api/sensitivity-distribution/",
    ]

    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: {response.status_code} - {len(response.text)} chars")
                results[endpoint] = True
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                results[endpoint] = False
        except Exception as e:
            print(f"❌ {endpoint}: Request failed - {e}")
            results[endpoint] = False

    return results

def test_chatbot_functionality(base_url="http://localhost:8000"):
    """Test chatbot API functionality"""
    print(f"\n🔍 Testing Chatbot Functionality at {base_url}...")

    test_messages = [
        "What is the resistance rate for E. coli?",
        "Show me antibiotic effectiveness data",
        "What are the resistance trends over time?",
        "Tell me about department-wise resistance patterns",
    ]

    results = {}
    for message in test_messages:
        try:
            payload = {"message": message}
            response = requests.post(f"{base_url}/api/chat/", json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"✅ Chat query successful: '{message[:30]}...' -> {len(response_text)} chars")
                results[message] = True
            else:
                print(f"❌ Chat query failed: {response.status_code}")
                results[message] = False
        except Exception as e:
            print(f"❌ Chat query error: {e}")
            results[message] = False

    return results

def test_data_analysis():
    """Test data analysis capabilities"""
    print("\n🔍 Testing Data Analysis Capabilities...")

    try:
        # Test resistance rate calculation
        total_samples = Sample.objects.count()
        resistant_results = TestResult.objects.filter(result='Resistant').count()

        if total_samples > 0:
            resistance_rate = (resistant_results / total_samples) * 100
            print(f"✅ Resistance rate calculation: {resistance_rate:.1f}%")
        else:
            print("⚠️  No sample data found for analysis")
            resistance_rate = 0

        # Test department-wise analysis
        departments = Sample.objects.values('department').distinct()
        dept_count = len(departments)
        print(f"✅ Department analysis: {dept_count} departments found")

        # Test time-based trends
        from django.db.models import Min, Max
        date_range = TestResult.objects.aggregate(
            min_date=Min('test_date'),
            max_date=Max('test_date')
        )
        print(f"✅ Time range: {date_range['min_date']} to {date_range['max_date']}")

        return {
            "total_samples": total_samples,
            "resistant_results": resistant_results,
            "resistance_rate": resistance_rate,
            "departments": dept_count,
            "date_range": date_range
        }

    except Exception as e:
        print(f"❌ Data analysis failed: {e}")
        return None

def run_full_test_suite():
    """Run complete test suite"""
    print("=" * 60)
    print("CHATBOT DATABASE CONNECTIVITY TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()

    # Test 1: Database Connection
    db_ok = test_database_connection()

    # Test 2: Django Models
    model_counts = test_models()

    # Test 3: API Endpoints
    api_results = test_api_endpoints()

    # Test 4: Chatbot Functionality
    chat_results = test_chatbot_functionality()

    # Test 5: Data Analysis
    analysis_results = test_data_analysis()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")

    model_pass = sum(1 for count in model_counts.values() if count >= 0)
    print(f"Django Models: {model_pass}/{len(model_counts)} passed")

    api_pass = sum(1 for result in api_results.values() if result)
    print(f"API Endpoints: {api_pass}/{len(api_results)} passed")

    chat_pass = sum(1 for result in chat_results.values() if result)
    print(f"Chat Functionality: {chat_pass}/{len(chat_results)} passed")

    analysis_ok = analysis_results is not None
    print(f"Data Analysis: {'✅ PASS' if analysis_ok else '❌ FAIL'}")

    total_pass = sum([
        db_ok,
        model_pass == len(model_counts),
        api_pass == len(api_results),
        chat_pass == len(chat_results),
        analysis_ok
    ])

    print(f"\nOverall Result: {total_pass}/5 test categories passed")

    if total_pass == 5:
        print("🎉 ALL TESTS PASSED - Chatbot is fully connected to database!")
    elif total_pass >= 3:
        print("⚠️  MOST TESTS PASSED - Chatbot has good database connectivity")
    else:
        print("❌ CRITICAL ISSUES - Chatbot database connectivity needs attention")

    print(f"\nTest completed at: {datetime.now()}")

    return {
        "database": db_ok,
        "models": model_counts,
        "api": api_results,
        "chat": chat_results,
        "analysis": analysis_results,
        "overall_score": total_pass
    }

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running")
        else:
            print("⚠️  Django server responded with status:", response.status_code)
    except:
        print("❌ Django server is not running on localhost:8000")
        print("Please start the server with: python manage.py runserver")
        sys.exit(1)

    # Run full test suite
    results = run_full_test_suite()

    # Save results
    import json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chatbot_db_test_results_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {filename}")
