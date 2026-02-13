#!/usr/bin/env python
"""
Test login functionality
"""
import os
import sys
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

def test_login(email, password):
    """Test login with given credentials"""
    url = 'http://127.0.0.1:8000/api/auth/token/'

    data = {
        'email': email,
        'password': password
    }

    try:
        response = requests.post(url, json=data)
        print(f"Testing login for {email}")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            print(f"User: {result.get('user', {}).get('email')}")
            print(f"Role: {result.get('user', {}).get('role')}")
            return True
        else:
            print("❌ Login failed!")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("Testing login credentials...")
    print("=" * 50)

    # Test admin user
    test_login('admin@hospital.com', 'admin123')
    print()

    # Test other users if they exist
    test_users = [
        ('admin@test.com', 'admin123'),
        ('doctor@test.com', 'doctor123'),
        ('lab@test.com', 'lab123'),
        ('viewer@test.com', 'viewer123'),
    ]

    for email, password in test_users:
        test_login(email, password)
        print()
