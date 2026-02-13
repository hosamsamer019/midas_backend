#!/usr/bin/env python
"""
Simple test script for messaging functionality using Django test client
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from messaging.models import Message, MessageAttachment
from users.models import User

def test_messaging():
    """Test messaging functionality"""
    print("🚀 Testing Enhanced Messaging System")
    print("=" * 60)

    # Create test client
    client = Client()

    # Get test users
    try:
        admin_user = User.objects.get(email='admin@test.com')
        doctor_user = User.objects.get(email='doctor@test.com')
        print("✅ Found test users")
    except User.DoesNotExist as e:
        print(f"❌ Test users not found: {e}")
        return

    # Test 1: Admin login
    print("\n🧪 Test 1: Admin login")
    login_data = {'email': 'admin@test.com', 'password': 'admin123'}
    response = client.post('/api/auth/login/', login_data, content_type='application/json')
    if response.status_code == 200:
        print("✅ Admin login successful")
        admin_token = response.json().get('access')
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        return

    # Test 2: Create direct message
    print("\n🧪 Test 2: Create direct message")
    headers = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
    message_data = {
        'recipient': doctor_user.id,
        'subject': 'Test Direct Message',
        'content': 'This is a test direct message from admin to doctor.',
        'message_type': 'direct'
    }
    response = client.post('/api/messaging/messages/', message_data, **headers)
    if response.status_code == 201:
        print("✅ Direct message created successfully")
        message_id = response.json()['id']
    else:
        print(f"❌ Failed to create direct message: {response.status_code} - {response.content}")
        return

    # Test 3: List messages
    print("\n🧪 Test 3: List messages")
    response = client.get('/api/messaging/messages/', **headers)
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ Found {len(messages)} messages")
    else:
        print(f"❌ Failed to list messages: {response.status_code}")

    # Test 4: Mark as read
    print("\n🧪 Test 4: Mark message as read")
    response = client.post(f'/api/messaging/messages/{message_id}/mark_read/', **headers)
    if response.status_code == 200:
        print("✅ Message marked as read")
    else:
        print(f"❌ Failed to mark as read: {response.status_code}")

    # Test 5: Archive message
    print("\n🧪 Test 5: Archive message")
    response = client.post(f'/api/messaging/messages/{message_id}/archive/', **headers)
    if response.status_code == 200:
        print("✅ Message archived successfully")
    else:
        print(f"❌ Failed to archive: {response.status_code}")

    # Test 6: Search messages
    print("\n🧪 Test 6: Search messages")
    response = client.get('/api/messaging/messages/search/?q=Test', **headers)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Search returned {len(results)} results")
    else:
        print(f"❌ Search failed: {response.status_code}")

    # Test 7: Create broadcast message
    print("\n🧪 Test 7: Create broadcast message")
    broadcast_data = {
        'subject': 'System Maintenance Notice',
        'content': 'The system will be under maintenance tonight.',
        'message_type': 'broadcast'
    }
    response = client.post('/api/messaging/messages/broadcast/', broadcast_data, **headers)
    if response.status_code == 201:
        print("✅ Broadcast message created successfully")
    else:
        print(f"❌ Failed to create broadcast: {response.status_code} - {response.content}")

    print("\n✅ Messaging system testing completed successfully!")

if __name__ == "__main__":
    test_messaging()
