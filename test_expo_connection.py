#!/usr/bin/env python3
"""
Test script to verify Expo device connectivity to the API
"""

import requests
import json

# Your local IP address (update this if it changes)
LOCAL_IP = "192.168.1.202"
API_BASE = f"http://{LOCAL_IP}:8000/api/v1"

def test_expo_connection():
    """Test API connectivity from Expo perspective"""
    print("🧪 Testing Expo Device Connection to API v1\n")
    
    # Test 1: Basic connectivity to events endpoint
    print("1. Testing basic API connectivity...")
    try:
        response = requests.get(f"{API_BASE}/events/")
        if response.status_code == 200:
            print("✅ API v1 is accessible!")
            events = response.json()
            print(f"   Found {len(events)} events")
        else:
            print(f"❌ API returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return
    
    print()
    
    # Test 2: CORS headers for Expo
    print("2. Testing CORS headers...")
    try:
        response = requests.options(
            f"{API_BASE}/events/",
            headers={
                'Origin': 'expo://192.168.1.243:8000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'X-Requested-With'
            }
        )
        
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-credentials': response.headers.get('access-control-allow-credentials'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
        }
        
        print("✅ CORS headers present:")
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
    
    print()
    
    # Test 3: Test with Expo user agent
    print("3. Testing with Expo user agent...")
    try:
        response = requests.get(
            f"{API_BASE}/events/",
            headers={
                'User-Agent': 'Expo/1.0.0',
                'Origin': 'expo://192.168.1.243:8000'
            }
        )
        if response.status_code == 200:
            print("✅ API accepts Expo user agent!")
        else:
            print(f"❌ API returned status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Expo user agent test failed: {e}")
    
    print()
    
    # Test 4: Test pagination parameters
    print("4. Testing pagination parameters...")
    try:
        response = requests.get(f"{API_BASE}/events/?page=1&limit=20")
        if response.status_code == 200:
            print("✅ Pagination parameters work!")
            events = response.json()
            print(f"   Response structure: {type(events)}")
        else:
            print(f"❌ Pagination test failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Pagination test failed: {e}")
    
    print()
    
    # Test 5: Test lat_lng format
    print("5. Testing lat_lng format...")
    try:
        response = requests.get(f"{API_BASE}/events/")
        if response.status_code == 200:
            events = response.json()
            if events and 'results' in events and events['results']:
                first_event = events['results'][0]
                if 'lat_lng' in first_event:
                    lat_lng = first_event['lat_lng']
                    if isinstance(lat_lng, dict) and 'latitude' in lat_lng and 'longitude' in lat_lng:
                        print("✅ lat_lng format is correct!")
                        print(f"   lat_lng: {lat_lng}")
                        print(f"   Type: {type(lat_lng)}")
                    else:
                        print(f"❌ lat_lng format is incorrect: {lat_lng}")
                else:
                    print("❌ lat_lng field not found in event")
            else:
                print("❌ No events found to test lat_lng format")
        else:
            print(f"❌ lat_lng test failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ lat_lng test failed: {e}")
    
    print()
    print("🎉 Expo connectivity test completed!")
    print(f"\n📱 Your Expo app can now connect to: {API_BASE}")
    print("   Make sure your Expo device is on the same network (192.168.1.x)")
    print("   API v1 endpoints are now available at /api/v1/")
    print("   lat_lng now returns: {{'latitude': 37.7749, 'longitude': -122.4194}}")

if __name__ == "__main__":
    test_expo_connection()
