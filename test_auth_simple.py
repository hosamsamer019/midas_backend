#!/usr/bin/env python
"""
Simple authentication test script
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_registration():
    """Test user registration"""
    print("🧪 Testing User Registration...")

    user_data = {
        "username": "test_admin",
        "email": "test_admin@example.com",
        "password": "admin123",
        "role": "admin"
    }

    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code == 201:
        print("✅ Registration successful")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code}")
        return False

def test_login():
    """Test login"""
    print("\n🧪 Testing Login...")

    login_data = {
        "email": "test_admin@example.com",
        "password": "admin123"
    }

    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get("access")
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_protected_endpoint(token):
    """Test access to protected endpoint"""
    print("\n🧪 Testing Protected Endpoint...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/", headers=headers)

    if response.status_code == 200:
        print("✅ Protected endpoint access successful")
        return True
    else:
        print(f"❌ Protected endpoint access failed: {response.status_code}")
        return False

def main():
    """Run simple authentication tests"""
    print("🚀 Starting Simple Authentication Tests")
    print("=" * 50)

    # Test registration
    if test_registration():
        # Test login
        token = test_login()
        if token:
            # Test protected access
            test_protected_endpoint(token)

    print("\n✅ Simple authentication testing completed!")

if __name__ == "__main__":
    main()
