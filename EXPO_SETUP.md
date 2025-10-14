# Expo Setup Guide for Django API

Your Django API is now configured to accept connections from Expo devices running on hardware!

## 🚀 What's Been Configured

1. **CORS Headers**: Added `django-cors-headers` to allow cross-origin requests
2. **Network Access**: Server now runs on `0.0.0.0:8000` to accept external connections
3. **Allowed Hosts**: Updated to accept connections from your local network
4. **CORS Settings**: Configured to allow all origins, methods, and headers needed for Expo
5. **API Versioning**: Added `/api/v1/` endpoints for better API management

## 📱 Expo Configuration

### 1. Update Your Expo App's API Base URL

In your Expo app, update the API base URL to use your computer's local IP with the v1 API:

```javascript
// Replace this:
const API_BASE = 'http://localhost:8000/api';

// With this:
const API_BASE = 'http://192.168.1.202:8000/api/v1';
```

### 2. Network Requirements

- **Same Network**: Your Expo device must be on the same WiFi network as your computer
- **Local IP**: Use `192.168.1.202:8000` (your computer's local IP)
- **Port**: Make sure port 8000 is not blocked by your firewall

### 3. Testing the Connection

You can test the connection using the provided test script:

```bash
python test_expo_connection.py
```

## 🔧 API Endpoints Available

Your Expo app can now access these **v1** endpoints:

- **Events**: `GET/POST http://192.168.1.202:8000/api/v1/events/`
- **Event Details**: `GET/PUT/PATCH/DELETE http://192.168.1.202:8000/api/v1/events/{id}/`
- **User Events**: `GET http://192.168.1.202:8000/api/v1/events/my-events/`
- **Nearby Events**: `GET http://192.168.1.202:8000/api/v1/events/nearby/`
- **Open Events**: `GET http://192.168.1.202:8000/api/v1/events/open/`
- **Accounts**: `http://192.168.1.202:8000/api/v1/accounts/`

### Legacy Endpoints (Still Available)

For backward compatibility, the old endpoints are still accessible:
- `http://192.168.1.202:8000/api/events/`
- `http://192.168.1.202:8000/api/accounts/`

## 🚨 Important Notes

1. **Development Only**: This configuration allows all origins (`CORS_ALLOW_ALL_ORIGINS = True`) - suitable for development only
2. **Security**: For production, you should restrict CORS to specific origins
3. **Network Changes**: If your local IP changes, update the API_BASE URL in your Expo app
4. **Firewall**: Ensure your computer's firewall allows incoming connections on port 8000
5. **API Versioning**: Use `/api/v1/` endpoints for new development, legacy endpoints remain available

## 🧪 Testing with Expo

1. Start your Django server: `python manage.py runserver 0.0.0.0:8000`
2. Make sure your Expo device is on the same WiFi network
3. Update your Expo app's API configuration to use `/api/v1/`
4. Test API calls from your Expo app

## 🔍 Troubleshooting

- **Connection Refused**: Check if Django server is running on `0.0.0.0:8000`
- **CORS Errors**: Verify `django-cors-headers` is installed and configured
- **Network Issues**: Ensure both devices are on the same network
- **Port Blocked**: Check if port 8000 is open in your firewall
- **404 Errors**: Make sure you're using the correct API version (`/api/v1/`)

## 📋 Migration Checklist

- [ ] Update Expo app API base URL to `/api/v1/`
- [ ] Test all API endpoints with new versioning
- [ ] Verify pagination parameters work (`?page=1&limit=20`)
- [ ] Check that admin-event relationships work correctly
- [ ] Ensure CORS is working for all endpoints

Your API is now versioned and ready for Expo devices! 🎉
