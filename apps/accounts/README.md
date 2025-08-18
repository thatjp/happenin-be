# Accounts API

This Django app provides a RESTful API for user authentication and profile management.

## API Endpoints

### Authentication

#### User Registration
- **POST** `/api/accounts/register/`
- **Description**: Create a new user account
- **Request Body**:
  ```json
  {
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "password": "securepassword",
    "password_confirm": "securepassword"
  }
  ```
- **Response**: Returns user data and authentication token

#### User Login
- **POST** `/api/accounts/login/`
- **Description**: Authenticate user and get token (accepts email or username)
- **Request Body**:
  ```json
  {
    "email_or_username": "johndoe@example.com",
    "password": "securepassword"
  }
  ```
  or
  ```json
  {
    "email_or_username": "johndoe",
    "password": "securepassword"
  }
  ```
- **Response**: Returns user data and authentication token

#### User Logout
- **POST** `/api/accounts/logout/`
- **Description**: Logout user and invalidate token
- **Authentication**: Required (Token)
- **Response**: Success message

### Profile Management

#### Get User Profile
- **GET** `/api/accounts/profile/`
- **Description**: Get current user's profile information
- **Authentication**: Required (Token)
- **Response**: User profile data

#### Update User Profile
- **PUT/PATCH** `/api/accounts/profile/`
- **Description**: Update current user's profile information
- **Authentication**: Required (Token)
- **Request Body**:
  ```json
  {
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01"
  }
  ```

#### Update User Profile Details
- **PUT/PATCH** `/api/accounts/profile/update/`
- **Description**: Update user profile details (bio, avatar, location, website)
- **Authentication**: Required (Token)
- **Request Body**:
  ```json
  {
    "bio": "Software developer passionate about technology",
    "location": "San Francisco, CA",
    "website": "https://johndoe.com"
  }
  ```

### Password Management

#### Change Password
- **POST** `/api/accounts/password/change/`
- **Description**: Change user password
- **Authentication**: Required (Token)
- **Request Body**:
  ```json
  {
    "old_password": "currentpassword",
    "new_password": "newpassword",
    "new_password_confirm": "newpassword"
  }
  ```

### Dashboard

#### User Dashboard
- **GET** `/api/accounts/dashboard/`
- **Description**: Get user dashboard information
- **Authentication**: Required (Token)
- **Response**: User data and statistics

### Admin

#### List Users
- **GET** `/api/accounts/users/`
- **Description**: List all users (admin only)
- **Authentication**: Required (Token + Staff permission)

## Authentication

The API uses Token-based authentication. Include the token in the Authorization header:

```
Authorization: Token your_token_here
```

## Response Format

All API responses follow this format:

```json
{
  "message": "Success message",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile": {
      "bio": "Software developer",
      "location": "San Francisco, CA",
      "website": "https://johndoe.com"
    }
  },
  "token": "your_auth_token"
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes and error messages:

```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## Usage Examples

### Using curl

```bash
# Register a new user
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"johndoe","email":"john@example.com","password":"password123","password_confirm":"password123","first_name":"John","last_name":"Doe"}'

# Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email_or_username":"johndoe@example.com","password":"password123"}'

# Get profile (with token)
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Token your_token_here"
```

### Using Python requests

```python
import requests

# Base URL
base_url = "http://localhost:8000/api/accounts"

# Register
response = requests.post(f"{base_url}/register/", json={
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe"
})

# Login
response = requests.post(f"{base_url}/login/", json={
    "email_or_username": "johndoe@example.com",
    "password": "password123"
})

token = response.json()['token']

# Get profile
headers = {"Authorization": f"Token {token}"}
response = requests.get(f"{base_url}/profile/", headers=headers)
```
