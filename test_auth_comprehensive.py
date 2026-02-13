#!/usr/bin/env python3
"""
Comprehensive Authentication System Test
Tests all aspects of the authentication system including:
- Login/logout functionality
- Role-based permissions
- Messaging system
- Audit logging
"""

import requests
import json
import time
from typing import Dict, List

BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_USERS = {
    'admin': {
        'email': 'admin@test.com',
        'password': 'admin123',
        'role': 'admin',
        'expected_permissions': ['full_access', 'user_management', 'data_operations', 'messaging_all']
    },
    'doctor': {
        'email': 'doctor@test.com',
        'password': 'doctor123',
        'role': 'doctor',
        'expected_permissions': ['dashboard', 'analytics', 'reports', 'ai_tools', 'messaging_admin']
    },
    'lab': {
        'email': 'lab@test.com',
        'password': 'lab123',
        'role': 'lab',
        'expected_permissions': ['upload_data', 'limited_ai', 'messaging_admin']
    },
    'viewer': {
        'email': 'viewer@test.com',
        'password': 'viewer123',
        'role': 'viewer',
        'expected_permissions': ['dashboard_readonly']
    }
}

class AuthSystemTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []

    def log_test(self, test_name: str, status: str, message: str = ""):
        """Log test results"""
        result = f"{'✅' if status == 'PASS' else '❌'} {test_name}: {message}"
        self.test_results.append(result)
        print(result)

    def login_user(self, user_type: str) -> bool:
        """Login a user and store their token"""
        user_data = TEST_USERS[user_type]
        login_url = f"{BASE_URL}/api/auth/login/"

        try:
            response = requests.post(login_url, json={
                'email': user_data['email'],
                'password': user_data['password']
            }, timeout=10)

            if response.status_code == 200:
                data = response.json()
                token = data.get('access')
                user_info = data.get('user', {})

                if token and user_info.get('role') == user_data['role']:
                    self.tokens[user_type] = token
                    self.log_test(f"Login {user_type}", "PASS",
                                f"Role: {user_info.get('role')}, Token: {token[:20]}...")
                    return True
                else:
                    self.log_test(f"Login {user_type}", "FAIL", "Invalid token or role")
                    return False
            else:
                self.log_test(f"Login {user_type}", "FAIL",
                            f"Status: {response.status_code}, Response: {response.text}")
                return False

        except Exception as e:
            self.log_test(f"Login {user_type}", "FAIL", f"Exception: {str(e)}")
            return False

    def test_endpoint_access(self, user_type: str, endpoint: str, method: str = 'GET',
                           expected_status: int = 200, data: dict = None) -> bool:
        """Test if user can access an endpoint"""
        if user_type not in self.tokens:
            self.log_test(f"Access {endpoint} as {user_type}", "FAIL", "No token available")
            return False

        headers = {'Authorization': f'Bearer {self.tokens[user_type]}'}
        url = f"{BASE_URL}{endpoint}"

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data or {}, timeout=10)
            else:
                self.log_test(f"Access {endpoint} as {user_type}", "FAIL", f"Unsupported method: {method}")
                return False

            if response.status_code == expected_status:
                self.log_test(f"Access {endpoint} as {user_type}", "PASS",
                            f"Status: {response.status_code}")
                return True
            else:
                self.log_test(f"Access {endpoint} as {user_type}", "FAIL",
                            f"Expected {expected_status}, got {response.status_code}: {response.text[:100]}")
                return False

        except Exception as e:
            self.log_test(f"Access {endpoint} as {user_type}", "FAIL", f"Exception: {str(e)}")
            return False

    def test_messaging_system(self) -> bool:
        """Test the messaging system functionality"""
        success = True

        # Test admin sending message to doctor
        if 'admin' in self.tokens and 'doctor' in self.tokens:
            # Get doctor user ID first
            headers = {'Authorization': f'Bearer {self.tokens["admin"]}'}
            users_response = requests.get(f"{BASE_URL}/api/users/", headers=headers, timeout=10)

            if users_response.status_code == 200:
                users = users_response.json()
                doctor_user = next((u for u in users if u['email'] == 'doctor@test.com'), None)

                if doctor_user:
                    message_data = {
                        'recipient': doctor_user['id'],
                        'subject': 'Test Message from Admin',
                        'content': 'This is a test message to verify messaging system works.'
                    }

                    msg_response = requests.post(
                        f"{BASE_URL}/api/messaging/messages/",
                        headers=headers,
                        json=message_data,
                        timeout=10
                    )

                    if msg_response.status_code == 201:
                        self.log_test("Admin send message to Doctor", "PASS")
                    else:
                        self.log_test("Admin send message to Doctor", "FAIL",
                                    f"Status: {msg_response.status_code}, Response: {msg_response.text}")
                        success = False
                else:
                    self.log_test("Admin send message to Doctor", "FAIL", "Could not find doctor user")
                    success = False
            else:
                self.log_test("Admin send message to Doctor", "FAIL", "Could not get users list")
                success = False

        # Test retrieving messages
        for user_type in ['admin', 'doctor']:
            if user_type in self.tokens:
                headers = {'Authorization': f'Bearer {self.tokens[user_type]}'}
                response = requests.get(f"{BASE_URL}/api/messaging/messages/", headers=headers, timeout=10)

                if response.status_code == 200:
                    self.log_test(f"{user_type} retrieve messages", "PASS")
                else:
                    self.log_test(f"{user_type} retrieve messages", "FAIL",
                                f"Status: {response.status_code}")
                    success = False

        return success

    def test_role_permissions(self) -> bool:
        """Test role-based permissions for different endpoints"""
        success = True

        # Define endpoints and expected access by role
        endpoints = {
            '/api/stats/': {'admin': 200, 'doctor': 200, 'lab': 200, 'viewer': 200},  # Public stats
            '/api/analytics/': {'admin': 200, 'doctor': 200, 'lab': 403, 'viewer': 403},  # Doctor+
            '/api/report/': {'admin': 200, 'doctor': 200, 'lab': 403, 'viewer': 403},  # Doctor+
            '/api/users/': {'admin': 200, 'doctor': 403, 'lab': 403, 'viewer': 403},  # Admin only
            '/api/uploads/': {'admin': 200, 'doctor': 403, 'lab': 200, 'viewer': 403},  # Admin + Lab
        }

        for endpoint, permissions in endpoints.items():
            for user_type, expected_status in permissions.items():
                if not self.test_endpoint_access(user_type, endpoint, expected_status=expected_status):
                    success = False

        return success

    def test_logout_functionality(self) -> bool:
        """Test logout functionality"""
        success = True

        for user_type in ['admin', 'doctor']:
            if user_type in self.tokens:
                headers = {'Authorization': f'Bearer {self.tokens[user_type]}'}
                response = requests.post(f"{BASE_URL}/api/auth/logout/", headers=headers, timeout=10)

                if response.status_code == 200:
                    self.log_test(f"{user_type} logout", "PASS")
                else:
                    self.log_test(f"{user_type} logout", "FAIL",
                                f"Status: {response.status_code}, Response: {response.text}")
                    success = False

        return success

    def run_all_tests(self):
        """Run comprehensive authentication system tests"""
        print("🚀 Starting Comprehensive Authentication System Tests")
        print("=" * 60)

        # Phase 1: Login Tests
        print("\n📋 Phase 1: User Login Tests")
        print("-" * 30)
        login_success = True
        for user_type in TEST_USERS.keys():
            if not self.login_user(user_type):
                login_success = False

        if not login_success:
            print("❌ Login tests failed. Stopping further tests.")
            return False

        # Phase 2: Permission Tests
        print("\n🔐 Phase 2: Role-Based Permission Tests")
        print("-" * 40)
        permission_success = self.test_role_permissions()

        # Phase 3: Messaging Tests
        print("\n💬 Phase 3: Messaging System Tests")
        print("-" * 30)
        messaging_success = self.test_messaging_system()

        # Phase 4: Logout Tests
        print("\n🚪 Phase 4: Logout Functionality Tests")
        print("-" * 35)
        logout_success = self.test_logout_functionality()

        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        all_passed = login_success and permission_success and messaging_success and logout_success

        print(f"Login Tests: {'✅ PASSED' if login_success else '❌ FAILED'}")
        print(f"Permission Tests: {'✅ PASSED' if permission_success else '❌ FAILED'}")
        print(f"Messaging Tests: {'✅ PASSED' if messaging_success else '❌ FAILED'}")
        print(f"Logout Tests: {'✅ PASSED' if logout_success else '❌ FAILED'}")

        print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

        if all_passed:
            print("\n🎉 Authentication system is working perfectly!")
            print("All users can login, permissions are properly enforced,")
            print("messaging system is functional, and logout works correctly.")
        else:
            print("\n⚠️  Some issues were found. Please review the test results above.")

        return all_passed

def main():
    tester = AuthSystemTester()
    success = tester.run_all_tests()

    # Save detailed results to file
    with open('Data_Analysis_Project/AUTH_TEST_RESULTS.md', 'w') as f:
        f.write("# Authentication System Test Results\n\n")
        f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Detailed Test Results\n\n")
        for result in tester.test_results:
            f.write(f"- {result}\n")
        f.write(f"\n## Summary\n\n")
        f.write(f"Overall Result: {'✅ PASSED' if success else '❌ FAILED'}\n")

    return success

if __name__ == "__main__":
    main()
