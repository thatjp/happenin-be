#!/usr/bin/env python3
"""
Test script for the happenin Events API
"""

import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000/api"
ACCOUNTS_URL = f"{BASE_URL}/accounts"
EVENTS_URL = f"{BASE_URL}/events"

def test_events_api():
    """Test the events API endpoints"""
    print("🧪 Testing happenin Events API\n")
    
    # First, we need to create a user and get a token
    print("1. Creating test user for events...")
    user_data = {
        "username": "eventuser",
        "email": "eventuser@example.com",
        "password": "eventpass123",
        "password_confirm": "eventpass123",
        "first_name": "Event",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{ACCOUNTS_URL}/register/", json=user_data)
        if response.status_code == 201:
            print("✅ User created successfully!")
            user_info = response.json()
            token = user_info.get('token')
            print(f"   User ID: {user_info['user']['id']}")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ User creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ User creation request failed: {e}")
        return
    
    print()
    
    # Set up headers for authenticated requests
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    # Test 2: Create an event
    print("2. Testing Event Creation...")
    event_data = {
        "title": "Summer Music Festival",
        "description": "A fantastic outdoor music festival with local bands",
        "address": "123 Park Street",
        "city": "San Francisco",
        "state": "CA",
        "country": "United States",
        "postal_code": "94102",
        "open_time": "14:00:00",  # 2:00 PM
        "close_time": "22:00:00",  # 10:00 PM
        "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "latitude": 37.7749,
        "longitude": -122.4194,
        "is_open": True,
        "is_active": True
    }
    
    try:
        response = requests.post(f"{EVENTS_URL}/", json=event_data, headers=headers)
        if response.status_code == 201:
            print("✅ Event created successfully!")
            event_info = response.json()
            event_id = event_info['id']
            print(f"   Event ID: {event_id}")
            print(f"   Title: {event_info['title']}")
            print(f"   City: {event_info['city']}")
        else:
            print(f"❌ Event creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Event creation request failed: {e}")
        return
    
    print()
    
    # Test 3: Get all events
    print("3. Testing Get All Events...")
    
    try:
        response = requests.get(f"{EVENTS_URL}/")
        if response.status_code == 200:
            print("✅ Events retrieved successfully!")
            events = response.json()
            print(f"   Total events: {len(events)}")
            if events:
                print(f"   First event: {events[0]['title']}")
        else:
            print(f"❌ Events retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Events retrieval request failed: {e}")
    
    print()
    
    # Test 4: Get specific event
    print("4. Testing Get Specific Event...")
    
    try:
        response = requests.get(f"{EVENTS_URL}/{event_id}/")
        if response.status_code == 200:
            print("✅ Event retrieved successfully!")
            event = response.json()
            print(f"   Title: {event['title']}")
            print(f"   Address: {event['full_address']}")
            print(f"   Coordinates: {event['lat_lng']}")
            print(f"   Currently Open: {event['is_currently_open']}")
        else:
            print(f"❌ Event retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Event retrieval request failed: {e}")
    
    print()
    
    # Test 5: Update event
    print("5. Testing Event Update...")
    update_data = {
        "title": "Summer Music Festival 2024",
        "description": "An amazing outdoor music festival with local and international bands"
    }
    
    try:
        response = requests.patch(f"{EVENTS_URL}/{event_id}/", json=update_data, headers=headers)
        if response.status_code == 200:
            print("✅ Event updated successfully!")
            updated_event = response.json()
            print(f"   Updated title: {updated_event['title']}")
            print(f"   Updated description: {updated_event['description']}")
        else:
            print(f"❌ Event update failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Event update request failed: {e}")
    
    print()
    
    # Test 6: Get user's events
    print("6. Testing Get User Events...")
    
    try:
        response = requests.get(f"{EVENTS_URL}/my-events/", headers=headers)
        if response.status_code == 200:
            print("✅ User events retrieved successfully!")
            user_events = response.json()
            print(f"   User events count: {len(user_events)}")
            if user_events:
                print(f"   First user event: {user_events[0]['title']}")
        else:
            print(f"❌ User events retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ User events retrieval request failed: {e}")
    
    print()
    
    # Test 7: Toggle event status
    print("7. Testing Toggle Event Status...")
    
    try:
        response = requests.post(f"{EVENTS_URL}/{event_id}/toggle-status/", headers=headers)
        if response.status_code == 200:
            print("✅ Event status toggled successfully!")
            result = response.json()
            print(f"   Message: {result['message']}")
            print(f"   New status: {'Open' if result['is_open'] else 'Closed'}")
        else:
            print(f"❌ Event status toggle failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Event status toggle request failed: {e}")
    
    print()
    
    # Test 8: Get nearby events
    print("8. Testing Get Nearby Events...")
    
    try:
        params = {
            'lat': 37.7749,
            'lng': -122.4194,
            'radius': 10
        }
        response = requests.get(f"{EVENTS_URL}/nearby/", params=params)
        if response.status_code == 200:
            print("✅ Nearby events retrieved successfully!")
            nearby_events = response.json()
            print(f"   Nearby events count: {len(nearby_events)}")
        else:
            print(f"❌ Nearby events retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Nearby events retrieval request failed: {e}")
    
    print()
    
    # Test 9: Get open events
    print("9. Testing Get Open Events...")
    
    try:
        response = requests.get(f"{EVENTS_URL}/open/")
        if response.status_code == 200:
            print("✅ Open events retrieved successfully!")
            open_events = response.json()
            print(f"   Open events count: {len(open_events)}")
        else:
            print(f"❌ Open events retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Open events retrieval request failed: {e}")
    
    print()
    
    # Test 10: Delete event
    print("10. Testing Event Deletion...")
    
    try:
        response = requests.delete(f"{EVENTS_URL}/{event_id}/", headers=headers)
        if response.status_code == 204:
            print("✅ Event deleted successfully!")
        else:
            print(f"❌ Event deletion failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Event deletion request failed: {e}")
    
    print()
    print("🎉 Events API testing completed!")

if __name__ == "__main__":
    test_events_api()
