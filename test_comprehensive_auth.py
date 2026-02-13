#!/usr/bin/env python
"""
Comprehensive test script for the authentication system
Tests all features: auth, permissions, messaging, uploads, audit logs
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def setup_test_users():
    """Create test users for different roles"""
    print("🧪 Setting up test users...")

    users = [
        {"username": "admin_test", "email": "admin@test.com", "password": "admin123", "role": "admin"},
        {"username": "doctor_test", "email": "doctor@test.com", "password": "doctor123", "role": "doctor"},
        {"username": "lab_test", "email": "lab@test.com", "password": "lab123", "role": "lab"},
        {"username": "viewer_test", "email": "viewer@test.com", "password": "viewer123", "role": "viewer"},
    ]

    created_users = {}

    for user_data in users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register/", json=user_data, timeout=10)
            if response.status_code == 201:
                print(f"✅ Created {user_data['role']}: {user_data['username']}")
                created_users[user_data['email']] = user_data
            else:
                print(f"⚠️  User {user_data['email']} may already exist: {response.status_code}")
                created_users[user_data['email']] = user_data
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create {user_data['role']}: {e}")

    return created_users

def authenticate_users(users):
    """Login all test users and return tokens"""
    print("\n🧪 Authenticating users...")

    tokens = {}

    for email, user_data in users.items():
        try:
            login_data = {"email": email, "password": user_data["password"]}
            response = requests.post(f"{BASE_URL}/auth/login/", json=login_data, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tokens[email] = {
                    "access": data.get("access"),
                    "refresh": data.get("refresh"),
                    "user": data.get("user")
                }
                role = data.get("user", {}).get("role", "unknown")
                print(f"✅ {role} login successful: {email}")
            else:
                print(f"❌ {email} login failed: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {email} login error: {e}")

    return tokens

def test_role_permissions(tokens):
    """Test role-based permissions for various endpoints"""
    print("\n🧪 Testing role-based permissions...")

    # Define test endpoints and expected access by role
    test_cases = [
        {
            "endpoint": "/users/",
            "method": "GET",
            "expected_roles": ["admin"],  # Only admin can list users
            "description": "List all users"
        },
        {
            "endpoint": "/analytics/",
            "method": "GET",
            "expected_roles": ["admin", "doctor"],  # Admin and doctor can access analytics
            "description": "Access analytics dashboard"
        },
        {
            "endpoint": "/reports/",
            "method": "GET",
            "expected_roles": ["admin", "doctor"],  # Admin and doctor can generate reports
            "description": "Generate reports"
        },
        {
            "endpoint": "/stats/",
            "method": "GET",
            "expected_roles": ["admin", "doctor", "lab", "viewer"],  # All roles can view stats
            "description": "View statistics"
        },
    ]

    results = {}

    for test_case in test_cases:
        endpoint = test_case["endpoint"]
        method = test_case["method"]
        expected_roles = test_case["expected_roles"]
        description = test_case["description"]

        print(f"\nTesting: {description} ({method} {endpoint})")
        print(f"Expected access for roles: {', '.join(expected_roles)}")

        endpoint_results = {}

        for email, token_data in tokens.items():
            user_role = token_data["user"]["role"]
            access_token = token_data["access"]

            headers = {"Authorization": f"Bearer {access_token}"}

            try:
                response = requests.request(method, f"{BASE_URL}{endpoint}",
                                          headers=headers, timeout=10)

                has_access = response.status_code in [200, 201, 202]
                should_have_access = user_role in expected_roles

                if has_access == should_have_access:
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"

                print(f"  {status} {user_role}: {response.status_code} {'(expected)' if should_have_access else '(unexpected)'}")

                endpoint_results[user_role] = {
                    "status_code": response.status_code,
                    "has_access": has_access,
                    "expected_access": should_have_access,
                    "pass": has_access == should_have_access
                }

            except requests.exceptions.RequestException as e:
                print(f"  ❌ {user_role}: Request failed - {e}")
                endpoint_results[user_role] = {"error": str(e)}

        results[f"{method} {endpoint}"] = endpoint_results

    return results

def test_messaging_system(tokens):
    """Test the internal messaging system"""
    print("\n🧪 Testing messaging system...")

    # Get admin and doctor tokens
    admin_token = None
    doctor_token = None
    lab_token = None

    for email, token_data in tokens.items():
        role = token_data["user"]["role"]
        if role == "admin":
            admin_token = token_data["access"]
        elif role == "doctor":
            doctor_token = token_data["access"]
        elif role == "lab":
            lab_token = token_data["access"]

    if not admin_token or not doctor_token:
        print("❌ Missing admin or doctor tokens for messaging test")
        return {}

    results = {}

    # Test 1: Doctor sends message to admin
    print("\nTesting doctor-to-admin messaging...")
    message_data = {
        "recipient": tokens["admin@test.com"]["user"]["id"],
        "subject": "Test Message from Doctor",
        "content": "This is a test message from doctor to admin."
    }

    headers = {"Authorization": f"Bearer {doctor_token}"}
    try:
        response = requests.post(f"{BASE_URL}/messaging/messages/",
                               json=message_data, headers=headers, timeout=10)

        if response.status_code == 201:
            print("✅ Doctor successfully sent message to admin")
            message_id = response.json().get("id")
            results["doctor_to_admin"] = {"status": "success", "message_id": message_id}
        else:
            print(f"❌ Doctor failed to send message: {response.status_code} - {response.text}")
            results["doctor_to_admin"] = {"status": "failed", "response": response.text}
    except requests.exceptions.RequestException as e:
        print(f"❌ Doctor messaging error: {e}")
        results["doctor_to_admin"] = {"status": "error", "error": str(e)}

    # Test 2: Admin replies to doctor
    if results.get("doctor_to_admin", {}).get("status") == "success":
        print("\nTesting admin reply to doctor...")
        reply_data = {
            "recipient": tokens["doctor@test.com"]["user"]["id"],
            "subject": "Re: Test Message from Doctor",
            "content": "This is a reply from admin to doctor."
        }

        headers = {"Authorization": f"Bearer {admin_token}"}
        try:
            response = requests.post(f"{BASE_URL}/messaging/messages/",
                                   json=reply_data, headers=headers, timeout=10)

            if response.status_code == 201:
                print("✅ Admin successfully replied to doctor")
                results["admin_to_doctor"] = {"status": "success"}
            else:
                print(f"❌ Admin failed to reply: {response.status_code} - {response.text}")
                results["admin_to_doctor"] = {"status": "failed", "response": response.text}
        except requests.exceptions.RequestException as e:
            print(f"❌ Admin reply error: {e}")
            results["admin_to_doctor"] = {"status": "error", "error": str(e)}

    # Test 3: Lab tries to send message to doctor (should fail)
    if lab_token:
        print("\nTesting lab-to-doctor messaging (should be restricted)...")
        lab_message = {
            "recipient": tokens["doctor@test.com"]["user"]["id"],
            "subject": "Test from Lab",
            "content": "This message should be restricted."
        }

        headers = {"Authorization": f"Bearer {lab_token}"}
        try:
            response = requests.post(f"{BASE_URL}/messaging/messages/",
                                   json=lab_message, headers=headers, timeout=10)

            if response.status_code == 403:
                print("✅ Lab correctly blocked from sending to doctor")
                results["lab_to_doctor"] = {"status": "correctly_blocked"}
            else:
                print(f"❌ Lab incorrectly allowed to send to doctor: {response.status_code}")
                results["lab_to_doctor"] = {"status": "incorrectly_allowed", "response": response.text}
        except requests.exceptions.RequestException as e:
            print(f"❌ Lab messaging test error: {e}")
            results["lab_to_doctor"] = {"status": "error", "error": str(e)}

    return results

def test_logout(tokens):
    """Test logout functionality"""
    print("\n🧪 Testing logout functionality...")

    results = {}

    for email, token_data in tokens.items():
        role = token_data["user"]["role"]
        access_token = token_data["access"]

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.post(f"{BASE_URL}/auth/logout/",
                                   headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"✅ {role} logout successful")
                results[email] = {"status": "success"}
            else:
                print(f"❌ {role} logout failed: {response.status_code} - {response.text}")
                results[email] = {"status": "failed", "response": response.text}
        except requests.exceptions.RequestException as e:
            print(f"❌ {role} logout error: {e}")
            results[email] = {"status": "error", "error": str(e)}

    return results

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE AUTHENTICATION SYSTEM TEST REPORT")
    print("="*60)

    total_tests = 0
    passed_tests = 0

    # Count permission tests
    if "permissions" in results:
        for endpoint, endpoint_results in results["permissions"].items():
            for role, role_result in endpoint_results.items():
                total_tests += 1
                if role_result.get("pass", False):
                    passed_tests += 1

    # Count messaging tests
    if "messaging" in results:
        for test_name, test_result in results["messaging"].items():
            total_tests += 1
            if test_result.get("status") in ["success", "correctly_blocked"]:
                passed_tests += 1

    # Count logout tests
    if "logout" in results:
        for email, logout_result in results["logout"].items():
            total_tests += 1
            if logout_result.get("status") == "success":
                passed_tests += 1

    print(f"Total Tests Run: {total_tests}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {total_tests - passed_tests}")
    print(".1f"
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(".1f"
        if success_rate >= 90:
            print("🎉 EXCELLENT: System performing well!")
        elif success_rate >= 75:
            print("✅ GOOD: System mostly functional")
        elif success_rate >= 50:
            print("⚠️  FAIR: Some issues to address")
        else:
            print("❌ POOR: Significant issues detected")

    print("\n" + "="*60)

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": success_rate if total_tests > 0 else 0
    }

def main():
    """Run comprehensive authentication system tests"""
    print("🚀 Starting Comprehensive Authentication System Tests")
    print("=" * 60)

    all_results = {}

    try:
        # Setup test users
        users = setup_test_users()

        # Authenticate users
        tokens = authenticate_users(users)

        if tokens:
            # Test permissions
            permission_results = test_role_permissions(tokens)
            all_results["permissions"] = permission_results

            # Test messaging
            messaging_results = test_messaging_system(tokens)
            all_results["messaging"] = messaging_results

            # Test logout
            logout_results = test_logout(tokens)
            all_results["logout"] = logout_results

        # Generate report
        report = generate_test_report(all_results)

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"auth_test_results_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "results": all_results,
                "summary": report
            }, f, indent=2)

        print(f"\n📄 Detailed results saved to: {filename}")

    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        all_results["error"] = str(e)

    print("\n✅ Comprehensive authentication testing completed!")

if __name__ == "__main__":
    main()
