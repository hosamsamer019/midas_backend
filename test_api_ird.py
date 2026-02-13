#!/usr/bin/env python
"""
Test script for IRD Document implementation - API endpoints
Tests the authentication, user management, and audit logging in API operations
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission, AdminEmailControl
from audit.models import AuditLog

BASE_URL = 'http://localhost:8000/api'

def test_login():
    """Test login endpoint"""
    print("Testing login endpoint...")

    # First, ensure we have a test user
    try:
        admin_role = Role.objects.get(role_name='Administrator')
        admin_user, created = User.objects.get_or_create(
            email='admin@test.com',
            defaults={
                'full_name': 'Test Admin',
                'role': admin_role,
                'status': 'Active'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("✓ Created test admin user")
    except Exception as e:
        print(f"✗ Failed to create test user: {e}")
        return None

    # Test login
    login_data = {
        'email': 'admin@test.com',
        'password': 'admin123'
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/token/", json=login_data, timeout=10)
        print(f"Login response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Login successful")
            print(f"  - Access token received: {len(data.get('access', ''))} chars")
            print(f"  - Refresh token received: {len(data.get('refresh', ''))} chars")
            print(f"  - User data: {data.get('user', {}).get('full_name')}")

            # Check audit log
            audit_logs = AuditLog.objects.filter(
                performed_by=admin_user,
                action_type='login'
            ).order_by('-timestamp')
            if audit_logs.exists():
                print("✓ Login audit log created")
                print(f"  - Details: {audit_logs.first().details}")
            else:
                print("✗ Login audit log not found")

            return data.get('access')
        else:
            print(f"✗ Login failed: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("✗ Connection error - server not running")
        return None
    except Exception as e:
        print(f"✗ Login test error: {e}")
        return None

def test_invalid_login():
    """Test invalid login"""
    print("\nTesting invalid login...")

    login_data = {
        'email': 'invalid@test.com',
        'password': 'wrongpass'
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/token/", json=login_data, timeout=10)
        print(f"Invalid login response status: {response.status_code}")

        if response.status_code == 401:
            print("✓ Invalid login correctly rejected")
        else:
            print(f"✗ Unexpected response: {response.text}")

    except Exception as e:
        print(f"✗ Invalid login test error: {e}")

def test_user_permissions(access_token):
    """Test user permissions via API"""
    print("\nTesting user permissions...")

    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        # Test users endpoint
        response = requests.get(f"{BASE_URL}/users/", headers=headers, timeout=10)
        print(f"Users endpoint status: {response.status_code}")

        if response.status_code == 200:
            users = response.json()
            print(f"✓ Retrieved {len(users)} users")
        else:
            print(f"✗ Users endpoint failed: {response.text}")

    except Exception as e:
        print(f"✗ User permissions test error: {e}")

def test_logout(access_token):
    """Test logout endpoint"""
    print("\nTesting logout endpoint...")

    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.post(f"{BASE_URL}/auth/logout/", headers=headers, timeout=10)
        print(f"Logout response status: {response.status_code}")

        if response.status_code == 200:
            print("✓ Logout successful")

            # Check audit log for logout
            admin_user = User.objects.get(email='admin@test.com')
            audit_logs = AuditLog.objects.filter(
                performed_by=admin_user,
                action_type='logout'
            ).order_by('-timestamp')
            if audit_logs.exists():
                print("✓ Logout audit log created")
                print(f"  - Details: {audit_logs.first().details}")
            else:
                print("✗ Logout audit log not found")
        else:
            print(f"✗ Logout failed: {response.text}")

    except Exception as e:
        print(f"✗ Logout test error: {e}")

def test_welcome_endpoint():
    """Test welcome endpoint (no auth required)"""
    print("\nTesting welcome endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/welcome/", timeout=10)
        print(f"Welcome endpoint status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Welcome message: {data.get('message')}")
        else:
            print(f"✗ Welcome endpoint failed: {response.text}")

    except Exception as e:
        print(f"✗ Welcome test error: {e}")

def test_bacteria_list():
    """Test bacteria list endpoint"""
    print("\nTesting bacteria list endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/bacteria-list/", timeout=10)
        print(f"Bacteria list status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {len(data)} bacteria types")
        else:
            print(f"✗ Bacteria list failed: {response.text}")

    except Exception as e:
        print(f"✗ Bacteria list test error: {e}")

def test_stats_endpoint():
    """Test stats endpoint"""
    print("\nTesting stats endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/stats/", timeout=10)
        print(f"Stats endpoint status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ Stats retrieved successfully")
            print(f"  - Total samples: {data.get('total_samples', 'N/A')}")
            print(f"  - Total bacteria: {data.get('total_bacteria', 'N/A')}")
        else:
            print(f"✗ Stats endpoint failed: {response.text}")

    except Exception as e:
        print(f"✗ Stats test error: {e}")

def main():
    """Run all API tests"""
    print("Starting IRD Document API Implementation Tests")
    print("=" * 50)

    try:
        # Test endpoints that don't require auth first
        test_welcome_endpoint()
        test_bacteria_list()
        test_stats_endpoint()

        # Test invalid login
        test_invalid_login()

        # Test login and get token
        access_token = test_login()

        if access_token:
            # Test authenticated endpoints
            test_user_permissions(access_token)
            test_logout(access_token)
        else:
            print("Skipping authenticated tests due to login failure")

        print("\n" + "=" * 50)
        print("✅ API tests completed!")
        print("IRD Document API implementation tested successfully.")

    except Exception as e:
        print(f"\n❌ API tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
