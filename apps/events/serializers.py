from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    lat_lng = serializers.SerializerMethodField()
    is_currently_open = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    created_by = serializers.SerializerMethodField()
    created_by_id = serializers.IntegerField(source='created_by.id', read_only=True)
    admins = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username'
    )
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'icon', 'price', 'is_free',
            'address', 'city', 'state', 'country', 'postal_code',
            'open_time', 'close_time', 'start_date', 'end_date', 'latitude', 'longitude',
            'is_open', 'is_active', 'lat_lng', 'is_currently_open', 'full_address',
            'created_at', 'updated_at', 'created_by', 'created_by_id', 'admins'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_id', 'is_currently_open', 'is_free']
    
    def get_lat_lng(self, obj):
        """Return latitude and longitude as a tuple"""
        return obj.lat_lng
    
    def get_created_by(self, obj):
        """Return created_by as an object with id and username"""
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'username': obj.created_by.username,
                'email': obj.created_by.email
            }
        return None
    
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
    admin_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of user IDs to set as admins'
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'icon', 'price', 'admin_ids',
            'address', 'city', 'state', 'country', 'postal_code',
            'open_time', 'close_time', 'start_date', 'end_date', 'latitude', 'longitude',
            'is_open', 'is_active'
        ]
    
    def create(self, validated_data):
        """Set the created_by field to the current user"""
        admin_ids = validated_data.pop('admin_ids', [])
        user = self.context['request'].user
        validated_data['created_by'] = user
        event = super().create(validated_data)
        # Add the creator as admin by default
        event.admins.add(user)
        if admin_ids:
            from apps.accounts.models import User
            admins = User.objects.filter(id__in=admin_ids)
            event.admins.add(*admins)
        return event


class EventUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating events"""
    admin_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of user IDs to set as admins'
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'icon', 'price', 'admin_ids',
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

    def update(self, instance, validated_data):
        admin_ids = validated_data.pop('admin_ids', None)
        instance = super().update(instance, validated_data)
        if admin_ids is not None:
            from apps.accounts.models import User
            admins = User.objects.filter(id__in=admin_ids)
            instance.admins.set(admins)
        return instance


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing events"""
    lat_lng = serializers.SerializerMethodField()
    is_currently_open = serializers.ReadOnlyField()
    full_address = serializers.ReadOnlyField()
    created_by = serializers.SerializerMethodField()
    created_by_id = serializers.IntegerField(source='created_by.id', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_type', 'icon', 'price', 'is_free', 'city', 
            'start_date', 'end_date', 'open_time', 'close_time',
            'latitude', 'longitude', 'is_open', 'is_active', 'lat_lng', 'is_currently_open',
            'full_address', 'created_by', 'created_by_id'
        ]
    
    def get_lat_lng(self, obj):
        """Return latitude and longitude as a tuple"""
        return obj.lat_lng
    
    def get_created_by(self, obj):
        """Return created_by as an object with id and username"""
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'username': obj.created_by.username,
                'email': obj.created_by.email
            }
        return None
