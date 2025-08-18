# Events API

This Django app provides a RESTful API for managing events with location, time, and status information.

## Event Model Properties

The Event model includes all the requested properties:

- **address**: Full address of the event
- **openTime**: Event opening time (`open_time` in the API)
- **closeTime**: Event closing time (`close_time` in the API)
- **latLng**: Latitude and longitude coordinates (`lat_lng` in the API)
- **isOpen**: Whether the event is currently open (`is_open` in the API)
- **isActive**: Whether the event is active/published (`is_active` in the API)

## API Endpoints

### Event Management

#### List/Create Events
- **GET** `/api/events/`
- **Description**: List all active events
- **Query Parameters**:
  - `city`: Filter by city
  - `state`: Filter by state
  - `country`: Filter by country
  - `is_open`: Filter by open status (true/false)
  - `start_date`: Filter events from this date (YYYY-MM-DD)
  - `end_date`: Filter events until this date (YYYY-MM-DD)
  - `lat`: Latitude for location-based filtering
  - `lng`: Longitude for location-based filtering
  - `radius`: Radius in kilometers for location filtering (default: 50)
  - `search`: Search in title, description, address, city
  - `ordering`: Order by start_date, created_at, title

- **POST** `/api/events/`
- **Description**: Create a new event
- **Authentication**: Required (Token)
- **Request Body**:
  ```json
  {
    "title": "Summer Music Festival",
    "description": "A fantastic outdoor music festival",
    "address": "123 Park Street",
    "city": "San Francisco",
    "state": "CA",
    "country": "United States",
    "postal_code": "94102",
    "open_time": "14:00:00",
    "close_time": "22:00:00",
    "start_date": "2024-08-23",
    "end_date": "2024-08-23",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "is_open": true,
    "is_active": true
  }
  ```

#### Event Details
- **GET** `/api/events/{id}/`
- **Description**: Get specific event details
- **Response**: Full event information including computed fields

- **PUT/PATCH** `/api/events/{id}/`
- **Description**: Update event details
- **Authentication**: Required (Token + Event creator)

- **DELETE** `/api/events/{id}/`
- **Description**: Delete an event
- **Authentication**: Required (Token + Event creator)

### User-Specific Endpoints

#### User Events
- **GET** `/api/events/my-events/`
- **Description**: List events created by the current user
- **Authentication**: Required (Token)

### Specialized Views

#### Nearby Events
- **GET** `/api/events/nearby/`
- **Description**: Find events near a specific location
- **Query Parameters**:
  - `lat`: Latitude (required)
  - `lng`: Longitude (required)
  - `radius`: Search radius in kilometers (default: 10)

#### Open Events
- **GET** `/api/events/open/`
- **Description**: List currently open events
- **Response**: Events that are currently open based on date and time

### Event Status Management

#### Toggle Event Status
- **POST** `/api/events/{id}/toggle-status/`
- **Description**: Toggle event open/closed status
- **Authentication**: Required (Token + Event creator)

#### Toggle Event Active
- **POST** `/api/events/{id}/toggle-active/`
- **Description**: Toggle event active/inactive status
- **Authentication**: Required (Token + Event creator)

## Computed Properties

The API provides several computed properties:

- **`lat_lng`**: Tuple of [latitude, longitude]
- **`is_currently_open`**: Boolean indicating if event is currently open (based on current date/time)
- **`full_address`**: Formatted complete address string

## Authentication

Most endpoints require authentication using token-based auth:

```
Authorization: Token your_token_here
```

## Response Format

### Event Object
```json
{
  "id": 1,
  "title": "Summer Music Festival",
  "description": "A fantastic outdoor music festival",
  "address": "123 Park Street",
  "city": "San Francisco",
  "state": "CA",
  "country": "United States",
  "postal_code": "94102",
  "open_time": "14:00:00",
  "close_time": "22:00:00",
  "start_date": "2024-08-23",
  "end_date": "2024-08-23",
  "latitude": "37.7749",
  "longitude": "-122.4194",
  "is_open": true,
  "is_active": true,
  "lat_lng": [37.7749, -122.4194],
  "is_currently_open": false,
  "full_address": "123 Park Street, San Francisco, CA, 94102, United States",
  "created_at": "2024-08-16T19:30:00Z",
  "updated_at": "2024-08-16T19:30:00Z",
  "created_by": "eventuser"
}
```

## Usage Examples

### Using curl

```bash
# Create an event
curl -X POST http://localhost:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{
    "title": "Tech Conference",
    "description": "Annual technology conference",
    "address": "456 Tech Blvd",
    "city": "San Jose",
    "state": "CA",
    "country": "United States",
    "open_time": "09:00:00",
    "close_time": "17:00:00",
    "start_date": "2024-09-15",
    "end_date": "2024-09-15",
    "latitude": 37.3382,
    "longitude": -121.8863,
    "is_open": true,
    "is_active": true
  }'

# Get all events
curl -X GET "http://localhost:8000/api/events/?city=San%20Francisco&is_open=true"

# Get nearby events
curl -X GET "http://localhost:8000/api/events/nearby/?lat=37.7749&lng=-122.4194&radius=10"
```

### Using Python requests

```python
import requests

# Base URL
base_url = "http://localhost:8000/api/events"
headers = {"Authorization": "Token your_token_here"}

# Create event
event_data = {
    "title": "Art Exhibition",
    "description": "Local artists showcase",
    "address": "789 Art Street",
    "city": "Oakland",
    "state": "CA",
    "country": "United States",
    "open_time": "10:00:00",
    "close_time": "18:00:00",
    "start_date": "2024-10-01",
    "end_date": "2024-10-01",
    "latitude": 37.8044,
    "longitude": -122.2711,
    "is_open": True,
    "is_active": True
}

response = requests.post(f"{base_url}/", json=event_data, headers=headers)
event = response.json()

# Get events in specific city
response = requests.get(f"{base_url}/?city=Oakland")
events = response.json()

# Find nearby events
params = {'lat': 37.8044, 'lng': -122.2711, 'radius': 5}
response = requests.get(f"{base_url}/nearby/", params=params)
nearby_events = response.json()
```

## Filtering and Search

The API supports comprehensive filtering:

- **Location-based**: Filter by city, state, country, or coordinates with radius
- **Time-based**: Filter by start/end dates
- **Status-based**: Filter by open/closed or active/inactive status
- **Text search**: Search in title, description, address, and city
- **Sorting**: Order by start date, creation date, or title

## Error Handling

Errors are returned with appropriate HTTP status codes:

```json
{
  "error": "Event not found or you do not have permission to modify it"
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `204`: Deleted
- `400`: Bad Request (validation errors)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found

## Testing

Run the test script to verify all endpoints:

```bash
python test_events_api.py
```

This will test all CRUD operations and specialized endpoints.
