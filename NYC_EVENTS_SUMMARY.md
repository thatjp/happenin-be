# NYC Events Summary

Your Django API now includes **15 diverse events** around New York City and Brooklyn! These events showcase the rich cultural diversity and vibrant atmosphere of NYC.

## 🗽 **Event Distribution by Borough**

- **New York City (Manhattan)**: 8 events
- **Brooklyn**: 6 events  
- **Queens**: 1 event
- **Total**: 20 events (including 5 original test events)

## 📍 **Events by Borough**

### **Manhattan (New York City)**

#### 🎵 **Music & Entertainment**
1. **Central Park Summer Concert Series**
   - Location: Central Park Great Lawn (40.7829, -73.9654)
   - Date: 3 days from today
   - Price: FREE
   - Type: Music, Outdoor Concert

2. **Greenwich Village Jazz Session**
   - Location: Village Vanguard (40.7355, -74.0027)
   - Date: 9 days from today
   - Price: $40
   - Type: Music, Jazz

3. **Times Square Comedy Night**
   - Location: Broadway & 42nd Street (40.7580, -73.9855)
   - Date: 2 days from today
   - Price: $35
   - Type: Entertainment, Comedy

#### 🎨 **Art & Culture**
4. **Chelsea Art Gallery Crawl**
   - Location: Chelsea Art District (40.7505, -74.0060)
   - Date: 4 days from today
   - Price: $30
   - Type: Art, Gallery Tour

5. **Upper West Side Literary Salon**
   - Location: Upper West Side (40.7870, -73.9754)
   - Date: 15 days from today
   - Price: $35
   - Type: Education, Literature

#### 🏗️ **Business & Education**
6. **Hudson Yards Tech Meetup**
   - Location: Hudson Yards (40.7505, -74.0060)
   - Date: 12 days from today
   - Price: $25
   - Type: Business, Technology

7. **Brooklyn Bridge Sunset Walk**
   - Location: Brooklyn Bridge Walkway (40.7061, -73.9969)
   - Date: 5 days from today
   - Price: $25
   - Type: Education, Walking Tour

8. **Manhattan Skyline Photography Workshop**
   - Location: Various Manhattan Locations (40.7589, -73.9851)
   - Date: 25 days from today
   - Price: $75
   - Type: Education, Photography

### **Brooklyn**

#### 🍕 **Food & Culture**
9. **Williamsburg Food Festival**
   - Location: McCarren Park (40.7182, -73.9582)
   - Date: 7-8 days from today
   - Price: $45
   - Type: Food, Festival

10. **Red Hook Seafood Festival**
    - Location: Red Hook Waterfront (40.6754, -74.0157)
    - Date: 18-19 days from today
    - Price: $30
    - Type: Food, Seafood

#### 🎨 **Arts & Entertainment**
11. **DUMBO Street Art Workshop**
    - Location: DUMBO Arts Center (40.7033, -73.9881)
    - Date: 6 days from today
    - Price: $55
    - Type: Art, Workshop

12. **Bushwick Street Dance Battle**
    - Location: Bushwick Collective (40.6943, -73.9207)
    - Date: 14 days from today
    - Price: FREE
    - Type: Entertainment, Dance

#### 🏛️ **History & Wellness**
13. **Brooklyn Heights Historical Tour**
    - Location: Brooklyn Heights Promenade (40.6995, -73.9934)
    - Date: 10 days from today
    - Price: $20
    - Type: Education, History

14. **Prospect Park Yoga & Wellness**
    - Location: Prospect Park Long Meadow (40.6602, -73.9690)
    - Date: Tomorrow
    - Price: $15
    - Type: Health, Yoga

### **Queens**

#### 🏺 **Cultural Festival**
15. **Astoria Greek Cultural Festival**
    - Location: Astoria Park (40.7829, -73.9207)
    - Date: 20-21 days from today
    - Price: $15
    - Type: Cultural, Greek Heritage

## 🎯 **Event Types Available**

- **Music**: 2 events
- **Education**: 4 events
- **Food**: 2 events
- **Entertainment**: 2 events
- **Art**: 2 events
- **Health**: 1 event
- **Business**: 1 event
- **Cultural**: 1 event

## 📱 **API Endpoints for NYC Events**

### **All Events**
```bash
GET /api/v1/events/
```

### **Events by City**
```bash
# Manhattan events
GET /api/v1/events/?city=New York

# Brooklyn events  
GET /api/v1/events/?city=Brooklyn

# Queens events
GET /api/v1/events/?city=Queens
```

### **Events by Type**
```bash
# Music events
GET /api/v1/events/?event_type=Music

# Food events
GET /api/v1/events/?event_type=Food

# Art events
GET /api/v1/events/?event_type=Art
```

### **Location-Based Search**
```bash
# Events near Times Square
GET /api/v1/events/nearby/?lat=40.7580&lng=-73.9855&radius=2

# Events near Central Park
GET /api/v1/events/nearby/?lat=40.7829&lng=-73.9654&radius=3

# Events near Williamsburg
GET /api/v1/events/nearby/?lat=40.7182&lng=-73.9582&radius=2
```

### **Pagination**
```bash
# First page with 10 events
GET /api/v1/events/?page=1&limit=10

# Second page with 10 events
GET /api/v1/events/?page=2&limit=10
```

## 🌟 **Key Features**

- **Realistic NYC Locations**: All events use actual NYC coordinates
- **Diverse Event Types**: Music, food, art, education, entertainment, health, business, cultural
- **Varied Pricing**: Free events to premium workshops ($0 - $75)
- **Future Dates**: Events scheduled from tomorrow to 25 days ahead
- **Proper Icons**: Each event type has appropriate icon representation
- **Admin Relationships**: All events have the creator set as an admin
- **Structured lat_lng**: Returns `{"latitude": 40.7829, "longitude": -73.9654}` format

## 🗺️ **Geographic Coverage**

- **Manhattan**: Central Park, Times Square, Chelsea, Greenwich Village, Upper West Side, Hudson Yards
- **Brooklyn**: Williamsburg, DUMBO, Brooklyn Heights, Prospect Park, Bushwick, Red Hook
- **Queens**: Astoria

## 🚀 **Perfect for Testing**

These events are ideal for testing:
- Location-based filtering
- Event type categorization
- Pagination
- Admin relationships
- CORS functionality
- API versioning

Your Expo app can now showcase a rich variety of NYC events with realistic locations and diverse content! 🎉
