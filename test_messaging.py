#!/usr/bin/env python
"""
Test script for the enhanced messaging system
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def login(email, password):
    """Login and return token"""
    login_data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        return response.json().get("access")
    return None

def test_messaging():
    """Test messaging functionality"""
    print("🚀 Testing Enhanced Messaging System")
    print("=" * 60)

    # Login as admin
    print("\n🧪 Logging in as admin...")
    admin_token = login("admin@test.com", "admin123")
    if not admin_token:
        print("❌ Admin login failed")
        return
    print("✅ Admin login successful")

    # Login as doctor
    print("\n🧪 Logging in as doctor...")
    doctor_token = login("doctor@test.com", "doctor123")
    if not doctor_token:
        print("❌ Doctor login failed")
        return
    print("✅ Doctor login successful")

    # Test 1: Admin sends direct message to doctor
    print("\n🧪 Test 1: Admin sends direct message to doctor")
    headers = {"Authorization": f"Bearer {admin_token}"}
    message_data = {
        "recipient": 2,  # doctor_user id
        "subject": "Test Direct Message",
        "content": "This is a test direct message from admin to doctor.",
        "message_type": "direct"
    }
    response = requests.post(f"{BASE_URL}/messaging/messages/", json=message_data, headers=headers)
    if response.status_code == 201:
        print("✅ Direct message sent successfully")
        message_id = response.json()['id']
    else:
        print(f"❌ Failed to send direct message: {response.status_code} - {response.text}")
        return

    # Test 2: Doctor reads the message
    print("\n🧪 Test 2: Doctor reads the message")
    headers_doctor = {"Authorization": f"Bearer {doctor_token}"}
    response = requests.patch(f"{BASE_URL}/messaging/messages/{message_id}/mark_read/", headers=headers_doctor)
    if response.status_code == 200:
        print("✅ Message marked as read")
    else:
        print(f"❌ Failed to mark as read: {response.status_code}")

    # Test 3: Admin sends broadcast message
    print("\n🧪 Test 3: Admin sends broadcast message")
    broadcast_data = {
        "subject": "System Maintenance Notice",
        "content": "The system will be under maintenance tonight.",
        "message_type": "broadcast"
    }
    response = requests.post(f"{BASE_URL}/messaging/messages/broadcast/", json=broadcast_data, headers=headers)
    if response.status_code == 201:
        print("✅ Broadcast message sent successfully")
    else:
        print(f"❌ Failed to send broadcast: {response.status_code} - {response.text}")

    # Test 4: Doctor tries to send broadcast (should fail)
    print("\n🧪 Test 4: Doctor tries to send broadcast (should fail)")
    response = requests.post(f"{BASE_URL}/messaging/messages/broadcast/", json=broadcast_data, headers=headers_doctor)
    if response.status_code == 403:
        print("✅ Broadcast permission correctly denied for doctor")
    else:
        print(f"❌ Broadcast permission not enforced: {response.status_code}")

    # Test 5: Search messages
    print("\n🧪 Test 5: Search messages")
    response = requests.get(f"{BASE_URL}/messaging/messages/search/?q=Test", headers=headers)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Search returned {len(results)} results")
    else:
        print(f"❌ Search failed: {response.status_code}")

    # Test 6: Archive message
    print("\n🧪 Test 6: Archive message")
    response = requests.post(f"{BASE_URL}/messaging/messages/{message_id}/archive/", headers=headers)
    if response.status_code == 200:
        print("✅ Message archived successfully")
    else:
        print(f"❌ Failed to archive: {response.status_code}")

    # Test 7: Check archived messages
    print("\n🧪 Test 7: Check archived messages")
    response = requests.get(f"{BASE_URL}/messaging/messages/archived/", headers=headers)
    if response.status_code == 200:
        archived = response.json()
        print(f"✅ Found {len(archived)} archived messages")
    else:
        print(f"❌ Failed to get archived: {response.status_code}")

    print("\n✅ Messaging system testing completed!")

if __name__ == "__main__":
    test_messaging()
