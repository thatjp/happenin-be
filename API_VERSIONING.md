# API Versioning Guide

## Overview

Your Django API now supports versioning to provide better API management and backward compatibility.

## Current API Versions

### API v1 (`/api/v1/`)
**Status**: Active Development
**Recommended for**: New Expo app development

**Available Endpoints:**
- `GET/POST /api/v1/events/` - List and create events
- `GET/PUT/PATCH/DELETE /api/v1/events/{id}/` - Event details and management
- `GET /api/v1/events/my-events/` - User's events (creator or admin)
- `GET /api/v1/events/nearby/` - Find events near a location
- `GET /api/v1/events/open/` - Currently open events
- `GET /api/v1/events/{id}/toggle-status/` - Toggle event open/closed
- `GET /api/v1/events/{id}/toggle-active/` - Toggle event active/inactive
- `GET/POST /api/v1/accounts/` - User account management

**Features:**
- ✅ CORS enabled for Expo devices
- ✅ Admin-event relationships
- ✅ Pagination support (`?page=1&limit=20`)
- ✅ Location-based filtering
- ✅ Event status management
- ✅ Structured lat_lng format: `{"latitude": 37.7749, "longitude": -122.4194}`

### Legacy API (`/api/`)
**Status**: Deprecated (but still functional)
**Recommended for**: Backward compatibility only

**Available Endpoints:**
- Same endpoints as v1 but without version prefix
- Will be removed in future versions

## Migration Guide

### For Expo Apps

1. **Update API Base URL:**
   ```javascript
   // Old
   const API_BASE = 'http://192.168.1.243:8000/api';
   
   // New
   const API_BASE = 'http://192.168.1.243:8000/api/v1';
   ```

2. **Update All Endpoint Calls:**
   ```javascript
   // Old
   fetch('http://192.168.1.243:8000/api/events/')
   
   // New
   fetch('http://192.168.1.243:8000/api/v1/events/')
   ```

### For Other Clients

- Update all API calls to use `/api/v1/` prefix
- Test pagination parameters work correctly
- Verify admin-event relationships function properly

## Versioning Strategy

### Current Version (v1)
- **Stability**: Stable API with consistent behavior
- **Features**: Full event management, admin relationships, CORS support
- **Support**: Full support and bug fixes

### Future Versions
- **v2**: Planned for major feature additions
- **v3**: Planned for breaking changes (if needed)

## Testing

### Test v1 Endpoints
```bash
# Test basic connectivity
curl "http://192.168.1.243:8000/api/v1/events/"

# Test pagination
curl "http://192.168.1.243:8000/api/v1/events/?page=1&limit=20"

# Test CORS
curl -H "Origin: expo://192.168.1.243:8000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS "http://192.168.1.243:8000/api/v1/events/"
```

### Run Full Test Suite
```bash
python test_expo_connection.py
```

## Benefits of Versioning

1. **Backward Compatibility**: Old clients continue to work
2. **Feature Evolution**: New features can be added without breaking existing apps
3. **Breaking Changes**: Future breaking changes can be introduced in new versions
4. **Client Migration**: Clients can migrate at their own pace
5. **API Documentation**: Clear separation of API capabilities by version

## Security Notes

- **CORS**: Currently allows all origins for development
- **Authentication**: Token-based authentication required for protected endpoints
- **Rate Limiting**: Consider adding rate limiting for production
- **Input Validation**: All endpoints validate input data

Your API is now properly versioned and ready for production use! 🚀
