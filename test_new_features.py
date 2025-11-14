import requests
import json
import os
from pathlib import Path

# Base URL for the API
BASE_URL = 'http://127.0.0.1:8000/api'

# Test credentials (you may need to adjust these)
TEST_USERNAME = 'admin'
TEST_PASSWORD = 'password123'  # Changed to match what we set

def get_auth_token():
    """Get authentication token for testing"""
    login_url = f"{BASE_URL}/auth/token/"
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD
    }

    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

# Global auth token
AUTH_TOKEN = None

def test_digital_signature():
    """Test digital signature creation and verification"""
    print("Testing Digital Signature functionality...")

    if not AUTH_TOKEN:
        print("❌ No auth token available, skipping digital signature test")
        return

    headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}

    # Sample document data
    document_data = {
        "report_title": "Antibiogram Report - October 2025",
        "total_samples": 150,
        "generated_by": "Dr. Smith",
        "timestamp": "2025-10-28T21:56:22Z"
    }

    # Convert to JSON string
    document_json = json.dumps(document_data, sort_keys=True)

    # 1. Sign the document
    sign_url = f"{BASE_URL}/digital-signature/"
    sign_response = requests.post(sign_url, json={"document_data": document_json}, headers=headers)

    if sign_response.status_code == 200:
        signature_data = sign_response.json()
        print("✅ Document signed successfully")
        print(f"   Signature: {signature_data['signature'][:50]}...")
        print(f"   Algorithm: {signature_data['algorithm']}")

        # 2. Verify the signature
        verify_response = requests.put(sign_url, json={
            "document_data": document_json,
            "signature": signature_data['signature'],
            "public_key": signature_data['public_key']
        }, headers=headers)

        if verify_response.status_code == 200:
            verify_result = verify_response.json()
            if verify_result['valid']:
                print("✅ Signature verification successful")
            else:
                print("❌ Signature verification failed")
        else:
            print(f"❌ Signature verification request failed: {verify_response.status_code}")

        # 3. Test with tampered data
        tampered_data = document_json.replace("150", "151")
        verify_tampered = requests.put(sign_url, json={
            "document_data": tampered_data,
            "signature": signature_data['signature'],
            "public_key": signature_data['public_key']
        }, headers=headers)

        if verify_tampered.status_code == 200:
            tampered_result = verify_tampered.json()
            if not tampered_result['valid']:
                print("✅ Tampered data correctly rejected")
            else:
                print("❌ Tampered data incorrectly accepted")
        else:
            print(f"❌ Tampered data verification request failed: {verify_tampered.status_code}")

    else:
        print(f"❌ Document signing failed: {sign_response.status_code}")
        print(f"   Response: {sign_response.text}")

def test_ocr_endpoint():
    """Test OCR endpoint (without actual image file)"""
    print("\nTesting OCR endpoint...")

    if not AUTH_TOKEN:
        print("❌ No auth token available, skipping OCR test")
        return

    headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}

    # Test without file (should return error)
    ocr_url = f"{BASE_URL}/ocr/"
    response = requests.post(ocr_url, headers=headers)

    if response.status_code == 400:
        print("✅ OCR endpoint correctly rejects requests without image")
    else:
        print(f"❌ OCR endpoint unexpected response: {response.status_code}")

def create_sample_image():
    """Create a simple sample image for OCR testing"""
    from PIL import Image, ImageDraw, ImageFont
    import os

    # Create a simple image with text
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Draw sample antibiogram text
    text = """Antibiogram Report
Bacteria: E. coli
Antibiotic: Ciprofloxacin
Result: Sensitive
MIC: 0.5 μg/mL"""

    draw.text((10, 10), text, fill='black', font=font)
    img.save('sample_antibiogram.png')
    print("✅ Sample image created: sample_antibiogram.png")
    return 'sample_antibiogram.png'

def test_ocr_with_sample():
    """Test OCR with a sample image"""
    print("\nTesting OCR with sample image...")

    if not AUTH_TOKEN:
        print("❌ No auth token available, skipping OCR test")
        return

    headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}

    # Create sample image
    image_path = create_sample_image()

    if os.path.exists(image_path):
        ocr_url = f"{BASE_URL}/ocr/"

        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(ocr_url, files=files, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("✅ OCR processing successful")
            print(f"   Extracted text: {result['text'][:100]}...")
            if 'data' in result:
                print(f"   Parsed data: {result['data']}")
        else:
            print(f"❌ OCR processing failed: {response.status_code}")
            print(f"   Response: {response.text}")

        # Clean up
        os.remove(image_path)
        print("✅ Sample image cleaned up")
    else:
        print("❌ Sample image creation failed")

def test_api_endpoints():
    """Test basic API endpoints to ensure system is working"""
    print("\nTesting basic API endpoints...")

    if not AUTH_TOKEN:
        print("❌ No auth token available, skipping authenticated endpoints")
        return

    headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}

    endpoints = [
        ('stats', 'GET'),
        ('analytics', 'GET'),
        ('sensitivity-distribution', 'GET'),
        ('antibiotic-effectiveness', 'GET'),
        ('resistance-over-time', 'GET'),
    ]

    for endpoint, method in endpoints:
        url = f"{BASE_URL}/{endpoint}/"
        if method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers)

        if response.status_code == 200:
            print(f"✅ {endpoint}: OK")
        else:
            print(f"❌ {endpoint}: {response.status_code}")

def main():
    """Run all tests"""
    print("🧪 Testing Smart Antibiogram System - New Features")
    print("=" * 60)

    global AUTH_TOKEN

    try:
        # Get authentication token first
        print("Getting authentication token...")
        AUTH_TOKEN = get_auth_token()
        if AUTH_TOKEN:
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed - some tests will be skipped")

        # Test basic endpoints first
        test_api_endpoints()

        # Test digital signature
        test_digital_signature()

        # Test OCR endpoint
        test_ocr_endpoint()
        test_ocr_with_sample()

        print("\n" + "=" * 60)
        print("🎉 Testing completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Django is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
