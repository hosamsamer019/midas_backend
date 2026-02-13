#!/usr/bin/env python
"""
Comprehensive Authentication and Database Testing
Tests all authentication endpoints, user roles, database connectivity, and audit logging
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.db import connection
from users.models import User, Role
from audit.models import AuditLog

BASE_URL = 'http://127.0.0.1:8000'

# Test user credentials
TEST_USERS = {
    'admin': {'email': 'admin@test.com', 'password': 'admin123', 'role': 'Administrator'},
    'doctor': {'email': 'doctor@test.com', 'password': 'doctor123', 'role': 'Doctor'},
    'lab': {'email': 'lab@test.com', 'password': 'lab123', 'role': 'Lab'},
    'viewer': {'email': 'viewer@test.com', 'password': 'viewer123', 'role': 'Viewer'},
}

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}

    def log(self, message, status='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {status}: {message}")

    def test_database_connection(self):
        """Test database connectivity"""
        self.log("Testing database connection...")
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                self.log("✅ Database connection successful", "SUCCESS")
                return True
            else:
                self.log("❌ Database query failed", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Database connection failed: {e}", "ERROR")
            return False

    def test_database_tables(self):
        """Test all required tables exist"""
        self.log("Testing database tables...")
        required_tables = [
            'users', 'roles', 'permissions', 'role_permissions',
            'admin_email_control', 'audit_auditlog'
        ]

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = []
            for table in required_tables:
                if table not in existing_tables:
                    missing_tables.append(table)

            if missing_tables:
                self.log(f"❌ Missing tables: {missing_tables}", "ERROR")
                return False
            else:
                self.log("✅ All required tables exist", "SUCCESS")
                return True
        except Exception as e:
            self.log(f"❌ Table check failed: {e}", "ERROR")
            return False

    def test_user_creation(self):
        """Test user creation and role assignment"""
        self.log("Testing user creation and roles...")
        try:
            # Check if users exist
            admin_user = User.objects.filter(email='admin@test.com').first()
            if admin_user:
                self.log(f"✅ Admin user exists: {admin_user.full_name} ({admin_user.role_id.role_name})", "SUCCESS")
            else:
                self.log("❌ Admin user not found", "ERROR")
                return False

            # Check roles
            roles = Role.objects.all()
            if roles.count() == 4:
                self.log(f"✅ All roles created: {[r.role_name for r in roles]}", "SUCCESS")
            else:
                self.log(f"❌ Expected 4 roles, found {roles.count()}", "ERROR")
                return False

            return True
        except Exception as e:
            self.log(f"❌ User creation test failed: {e}", "ERROR")
            return False

    def test_login(self, user_type):
        """Test login for specific user type"""
        user_data = TEST_USERS[user_type]
        self.log(f"Testing login for {user_type}...")

        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/token/",
                json={
                    'email': user_data['email'],
                    'password': user_data['password']
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = {
                    'access': data.get('access'),
                    'refresh': data.get('refresh'),
                    'user': data.get('user')
                }

                user_info = data.get('user', {})
                role = user_info.get('role', 'Unknown')
                email = user_info.get('email', 'Unknown')

                if role == user_data['role']:
                    self.log(f"✅ {user_type.title()} login successful: {email} ({role})", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Role mismatch: expected {user_data['role']}, got {role}", "ERROR")
                    return False
            else:
                self.log(f"❌ {user_type.title()} login failed: HTTP {response.status_code} - {response.text}", "ERROR")
                return False

        except requests.exceptions.RequestException as e:
            self.log(f"❌ {user_type.title()} login error: {e}", "ERROR")
            return False

    def test_logout(self, user_type):
        """Test logout for specific user type"""
        if user_type not in self.tokens:
            self.log(f"❌ Cannot test logout for {user_type}: no token available", "ERROR")
            return False

        self.log(f"Testing logout for {user_type}...")

        try:
            headers = {'Authorization': f"Bearer {self.tokens[user_type]['access']}"}
            response = self.session.post(f"{BASE_URL}/api/auth/logout/", headers=headers, timeout=10)

            if response.status_code == 200:
                self.log(f"✅ {user_type.title()} logout successful", "SUCCESS")
                return True
            else:
                self.log(f"❌ {user_type.title()} logout failed: HTTP {response.status_code} - {response.text}", "ERROR")
                return False

        except requests.exceptions.RequestException as e:
            self.log(f"❌ {user_type.title()} logout error: {e}", "ERROR")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        self.log("Testing invalid login scenarios...")

        test_cases = [
            {'email': 'invalid@test.com', 'password': 'wrongpass', 'description': 'Invalid email'},
            {'email': 'admin@test.com', 'password': 'wrongpass', 'description': 'Wrong password'},
            {'email': '', 'password': 'admin123', 'description': 'Empty email'},
            {'email': 'admin@test.com', 'password': '', 'description': 'Empty password'},
        ]

        all_passed = True
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{BASE_URL}/api/auth/token/",
                    json={
                        'email': test_case['email'],
                        'password': test_case['password']
                    },
                    timeout=10
                )

                if response.status_code == 401:
                    self.log(f"✅ {test_case['description']}: Correctly rejected (401)", "SUCCESS")
                else:
                    self.log(f"❌ {test_case['description']}: Expected 401, got {response.status_code}", "ERROR")
                    all_passed = False

            except requests.exceptions.RequestException as e:
                self.log(f"❌ {test_case['description']}: Request error: {e}", "ERROR")
                all_passed = False

        return all_passed

    def test_audit_logging(self):
        """Test audit logging functionality"""
        self.log("Testing audit logging...")

        try:
            # Count audit logs before login
            initial_count = AuditLog.objects.count()

            # Perform a login
            self.test_login('admin')

            # Count audit logs after login
            after_count = AuditLog.objects.count()

            if after_count > initial_count:
                # Check the latest log
                latest_log = AuditLog.objects.order_by('-timestamp').first()
                if latest_log and latest_log.action_type == 'login':
                    self.log("✅ Audit logging working: Login event recorded", "SUCCESS")
                    return True
                else:
                    self.log("❌ Audit log created but wrong action type", "ERROR")
                    return False
            else:
                self.log("❌ No audit log created for login", "ERROR")
                return False

        except Exception as e:
            self.log(f"❌ Audit logging test failed: {e}", "ERROR")
            return False

    def test_role_based_access(self):
        """Test role-based access control"""
        self.log("Testing role-based access control...")

        # Test endpoints that require different permissions
        test_endpoints = [
            {'url': '/api/users/', 'method': 'GET', 'required_role': 'Administrator'},
            {'url': '/api/stats/', 'method': 'GET', 'required_role': 'Any'},
        ]

        all_passed = True
        for endpoint in test_endpoints:
            for user_type in ['admin', 'doctor', 'lab', 'viewer']:
                if user_type in self.tokens:
                    headers = {'Authorization': f"Bearer {self.tokens[user_type]['access']}"}

                    try:
                        response = self.session.request(
                            endpoint['method'],
                            f"{BASE_URL}{endpoint['url']}",
                            headers=headers,
                            timeout=10
                        )

                        user_role = TEST_USERS[user_type]['role']
                        should_have_access = (
                            endpoint['required_role'] == 'Any' or
                            user_role == endpoint['required_role'] or
                            user_role == 'Administrator'
                        )

                        if should_have_access and response.status_code in [200, 201]:
                            self.log(f"✅ {user_type} correctly accessed {endpoint['url']}", "SUCCESS")
                        elif not should_have_access and response.status_code in [403, 401]:
                            self.log(f"✅ {user_type} correctly denied access to {endpoint['url']}", "SUCCESS")
                        elif should_have_access and response.status_code not in [200, 201]:
                            self.log(f"❌ {user_type} should have access to {endpoint['url']} but got {response.status_code}", "ERROR")
                            all_passed = False
                        elif not should_have_access and response.status_code not in [403, 401]:
                            self.log(f"❌ {user_type} should be denied access to {endpoint['url']} but got {response.status_code}", "ERROR")
                            all_passed = False

                    except requests.exceptions.RequestException as e:
                        self.log(f"❌ {user_type} request to {endpoint['url']} failed: {e}", "ERROR")
                        all_passed = False

        return all_passed

    def run_all_tests(self):
        """Run all authentication and database tests"""
        self.log("=" * 60)
        self.log("COMPREHENSIVE AUTHENTICATION & DATABASE TESTING")
        self.log("=" * 60)

        test_results = {}

        # Database tests
        test_results['database_connection'] = self.test_database_connection()
        test_results['database_tables'] = self.test_database_tables()
        test_results['user_creation'] = self.test_user_creation()

        # Authentication tests
        test_results['admin_login'] = self.test_login('admin')
        test_results['doctor_login'] = self.test_login('doctor')
        test_results['lab_login'] = self.test_login('lab')
        test_results['viewer_login'] = self.test_login('viewer')

        test_results['invalid_login'] = self.test_invalid_login()

        # Logout tests
        test_results['admin_logout'] = self.test_logout('admin')
        test_results['doctor_logout'] = self.test_logout('doctor')

        # Advanced tests
        test_results['audit_logging'] = self.test_audit_logging()
        test_results['role_based_access'] = self.test_role_based_access()

        # Summary
        self.log("\n" + "=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)

        passed = 0
        total = len(test_results)

        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1

        self.log(f"\nOVERALL RESULT: {passed}/{total} tests passed")

        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Authentication system is fully functional.", "SUCCESS")
            return True
        else:
            self.log(f"⚠️  {total - passed} tests failed. Please review the issues above.", "WARNING")
            return False

def main():
    tester = AuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
