from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    lat_lng = serializers.SerializerMethodField()
    is_currently_open = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'icon', 'price', 'is_free',
            'address', 'city', 'state', 'country', 'postal_code',
            'open_time', 'close_time', 'start_date', 'end_date', 'latitude', 'longitude',
            'is_open', 'is_active', 'lat_lng', 'is_currently_open', 'full_address',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'is_currently_open', 'is_free']
    
    def get_lat_lng(self, obj):
        """Return latitude and longitude as a tuple"""
        return obj.lat_lng
    
    def validate(self, attrs):
        """Validate event data"""
        # Ensure end_date is not before start_date
        if 'start_date' in attrs and 'end_date' in attrs:
            if attrs['end_date'] < attrs['start_date']:
                raise serializers.ValidationError("End date cannot be before start date")
        
        # Ensure close_time is not before open_time (unless it's overnight)
        if 'open_time' in attrs and 'close_time' in attrs:
            # This is allowed for overnight events, so we won't validate it strictly
            pass
        
        return attrs


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'icon', 'price',
            'address', 'city', 'state', 'country', 'postal_code',
            'open_time', 'close_time', 'start_date', 'end_date', 'latitude', 'longitude',
            'is_open', 'is_active'
        ]
    
    def create(self, validated_data):
        """Set the created_by field to the current user"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class EventUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating events"""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'icon', 'price',
            'address', 'city', 'state', 'country', 'postal_code',
            'open_time', 'close_time', 'start_date', 'end_date', 'latitude', 'longitude',
            'is_open', 'is_active'
        ]
    
    def validate(self, attrs):
        """Validate event data"""
        # Ensure end_date is not before start_date
        if 'start_date' in attrs and 'end_date' in attrs:
            if attrs['end_date'] < attrs['start_date']:
                raise serializers.ValidationError("End date cannot be before start date")
        
        return attrs


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing events"""
    lat_lng = serializers.SerializerMethodField()
    is_currently_open = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_type', 'icon', 'price', 'is_free', 'city', 
            'start_date', 'end_date', 'open_time', 'close_time',
            'latitude', 'longitude', 'is_open', 'is_active', 'lat_lng', 'is_currently_open',
            'full_address'
        ]
    
    def get_lat_lng(self, obj):
        """Return latitude and longitude as a tuple"""
        return obj.lat_lng
