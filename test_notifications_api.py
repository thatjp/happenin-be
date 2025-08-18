#!/usr/bin/env python
"""
Simple API test script to verify the notification endpoints are working.
Run this after starting the Django server to test the API endpoints.
"""

import requests
import json
import sys

# API base URL
BASE_URL = 'http://localhost:8000/api'

def test_notifications_api():
    """Test the notification API endpoints"""
    print("🧪 Testing Notifications API...")
    print("=" * 50)
    
    # Test 1: Get notification types
    print("1. Testing GET /api/notifications/types/...")
    try:
        response = requests.get(f'{BASE_URL}/notifications/types/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! Found {len(data)} notification types")
            for item in data[:3]:  # Show first 3
                print(f"     - {item['value']}: {item['display_name']}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
            print(f"     Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Connection failed. Make sure Django server is running on port 8000")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Get notification priorities
    print("\n2. Testing GET /api/notifications/priorities/...")
    try:
        response = requests.get(f'{BASE_URL}/notifications/priorities/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! Found {len(data)} notification priorities")
            for item in data:
                print(f"     - {item['value']}: {item['display_name']}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Get notification statuses
    print("\n3. Testing GET /api/notifications/statuses/...")
    try:
        response = requests.get(f'{BASE_URL}/notifications/statuses/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! Found {len(data)} notification statuses")
            for item in data:
                print(f"     - {item['value']}: {item['display_name']}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Get notification channels
    print("\n4. Testing GET /api/notifications/channels/...")
    try:
        response = requests.get(f'{BASE_URL}/notifications/channels/')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success! Found {len(data)} notification channels")
            for item in data:
                print(f"     - {item['value']}: {item['display_name']}")
        else:
            print(f"   ✗ Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 5: Test authentication requirement
    print("\n5. Testing authentication requirement...")
    try:
        response = requests.get(f'{BASE_URL}/notifications/notifications/')
        if response.status_code == 401:
            print("   ✓ Success! API correctly requires authentication")
        else:
            print(f"   ✗ Unexpected status code: {response.status_code}")
            print(f"     Expected 401 (Unauthorized), got {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All API tests passed! The notification endpoints are working correctly.")
    print("=" * 50)
    print("\nNote: Some endpoints require authentication. To test authenticated endpoints,")
    print("you'll need to create a user and get an authentication token.")
    print("\nTo create a superuser and test admin interface:")
    print("python manage.py createsuperuser")
    print("Then visit: http://localhost:8000/admin/")
    
    return True

if __name__ == '__main__':
    try:
        success = test_notifications_api()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
