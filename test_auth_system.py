#!/usr/bin/env python
"""
Test script for the authentication system
Tests login/logout, permissions, and audit logging
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_registration():
    """Test user registration"""
    print("🧪 Testing User Registration...")

    # Test data for different roles
    users = [
        {"username": "admin_test", "email": "admin@test.com", "password": "admin123", "role": "admin"},
        {"username": "doctor_test", "email": "doctor@test.com", "password": "doctor123", "role": "doctor"},
        {"username": "lab_test", "email": "lab@test.com", "password": "lab123", "role": "lab"},
        {"username": "viewer_test", "email": "viewer@test.com", "password": "viewer123", "role": "viewer"},
    ]

    for user_data in users:
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        if response.status_code == 201:
            print(f"✅ Registered {user_data['role']}: {user_data['username']}")
        else:
            print(f"❌ Failed to register {user_data['role']}: {response.text}")

def test_login():
    """Test login with different users"""
    print("\n🧪 Testing Login...")

    users = [
        {"email": "admin@test.com", "password": "admin123"},
        {"email": "doctor@test.com", "password": "doctor123"},
        {"email": "lab@test.com", "password": "lab123"},
        {"email": "viewer@test.com", "password": "viewer123"},
    ]

    tokens = {}

    for user in users:
        response = requests.post(f"{BASE_URL}/auth/login/", json=user)
        if response.status_code == 200:
            data = response.json()
            tokens[user['email']] = data.get('access')
            print(f"✅ Login successful for {user['email']}")
            print(f"   Role: {data['user']['role']}")
        else:
            print(f"❌ Login failed for {user['email']}: {response.text}")

    return tokens

def test_permissions(tokens):
    """Test role-based permissions"""
    print("\n🧪 Testing Role-Based Permissions...")

    endpoints = [
        ("GET", "/users/", "admin"),
        ("GET", "/analytics/", "doctor"),
        ("GET", "/uploads/", "lab"),
        ("GET", "/stats/", "viewer"),
    ]

    for method, endpoint, required_role in endpoints:
        print(f"\nTesting {method} {endpoint} (requires {required_role})")

        for email, token in tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers)

            # Get user role from email
            role = email.split('@')[0].replace('_test', '')

            if role == required_role or role == 'admin':
                expected_status = 200
            elif role == 'doctor' and required_role in ['doctor', 'lab', 'viewer']:
                expected_status = 200
            elif role == 'lab' and required_role == 'viewer':
                expected_status = 200
            else:
                expected_status = 403

            if response.status_code == expected_status:
                print(f"✅ {role} -> {response.status_code} (expected)")
            else:
                print(f"❌ {role} -> {response.status_code} (expected {expected_status})")

def test_logout(tokens):
    """Test logout functionality"""
    print("\n🧪 Testing Logout...")

    for email, token in tokens.items():
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/auth/logout/", headers=headers)

        if response.status_code == 200:
            print(f"✅ Logout successful for {email}")
        else:
            print(f"❌ Logout failed for {email}: {response.text}")

def test_audit_logs():
    """Test audit logging"""
    print("\n🧪 Testing Audit Logs...")

    # This would require admin access to view audit logs
    # For now, just check if the endpoint exists
    response = requests.get(f"{BASE_URL}/audit/logs/")
    print(f"Audit logs endpoint status: {response.status_code}")

def main():
    """Run all authentication tests"""
    print("🚀 Starting Authentication System Tests")
    print("=" * 50)

    try:
        # Test registration
        test_registration()

        # Test login
        tokens = test_login()

        if tokens:
            # Test permissions
            test_permissions(tokens)

            # Test logout
            test_logout(tokens)

        # Test audit logs
        test_audit_logs()

        print("\n" + "=" * 50)
        print("✅ Authentication system tests completed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
