#!/usr/bin/env python3
"""
Test script for the Happin Accounts API
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/accounts"

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing Happin Accounts API\n")
    
    # Test 1: User Registration
    print("1. Testing User Registration...")
    registration_data = {
        "username": "testuser9",
        "email": "test9@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        if response.status_code == 201:
            print("✅ Registration successful!")
            user_data = response.json()
            token = user_data.get('token')
            print(f"   User ID: {user_data['user']['id']}")
            print(f"   Username: {user_data['user']['username']}")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration request failed: {e}")
        return
    
    print()
    
    # Test 2: User Login
    print("2. Testing User Login...")
    login_data = {
        "email_or_username": "test9@example.com",  # Can use email or username
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful!")
            login_response = response.json()
            token = login_response.get('token')
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return
    
    print()
    
    # Test 3: Get User Profile (requires authentication)
    print("3. Testing Get User Profile...")
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        if response.status_code == 200:
            print("✅ Profile retrieval successful!")
            profile_data = response.json()
            print(f"   Username: {profile_data['username']}")
            print(f"   Email: {profile_data['email']}")
            print(f"   Full Name: {profile_data['first_name']} {profile_data['last_name']}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Profile request failed: {e}")
    
    print()
    
    # Test 4: Update User Profile
    print("4. Testing Update User Profile...")
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    try:
        response = requests.patch(f"{BASE_URL}/profile/", json=update_data, headers=headers)
        if response.status_code == 200:
            print("✅ Profile update successful!")
            updated_data = response.json()
            print(f"   Updated Name: {updated_data['first_name']} {updated_data['last_name']}")
        else:
            print(f"❌ Profile update failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Profile update request failed: {e}")
    
    print()
    
    # Test 5: Get User Dashboard
    print("5. Testing Get User Dashboard...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
        if response.status_code == 200:
            print("✅ Dashboard retrieval successful!")
            dashboard_data = response.json()
            print(f"   Member since: {dashboard_data['stats']['member_since']}")
            print(f"   Last login: {dashboard_data['stats']['last_login']}")
            print(f"   Verified: {dashboard_data['stats']['is_verified']}")
        else:
            print(f"❌ Dashboard retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard request failed: {e}")
    
    print()
    
    # Test 6: User Logout
    print("6. Testing User Logout...")
    
    try:
        response = requests.post(f"{BASE_URL}/logout/", headers=headers)
        if response.status_code == 200:
            print("✅ Logout successful!")
            print(f"   Response: {response.json()['message']}")
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Logout request failed: {e}")
    
    print()
    print("🎉 API testing completed!")

if __name__ == "__main__":
    test_api()
