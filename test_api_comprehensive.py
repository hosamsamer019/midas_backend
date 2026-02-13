"""
Comprehensive API test to verify analysis data is accessible
"""
import os
import django
import requests

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from rest_framework_simplejwt.tokens import AccessToken
from users.models import User

# Get the first user and generate token
user = User.objects.first()
if user:
    token = str(AccessToken.for_user(user))
    print(f"Generated token: {token[:50]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test endpoints
    endpoints = [
        '/api/stats/',
        '/api/sensitivity/',
        '/api/effectiveness/',
        '/api/bacteria/',
        '/api/antibiotics/',
        '/api/samples/',
    ]
    
    base_url = 'http://127.0.0.1:8000'
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, headers=headers, timeout=10)
            print(f"\n{endpoint}")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
                    # Print first few keys and values
                    for key in list(data.keys())[:3]:
                        print(f"  {key}: {data[key]}")
                elif isinstance(data, list):
                    print(f"  List length: {len(data)}")
                    if len(data) > 0:
                        print(f"  First item: {data[0]}")
            else:
                print(f"  Error: {response.text[:100]}")
        except requests.exceptions.ConnectionError:
            print(f"\n{endpoint}")
            print(f"  Error: Could not connect to server")
        except Exception as e:
            print(f"\n{endpoint}")
            print(f"  Error: {str(e)}")
else:
    print("No user found in database")
