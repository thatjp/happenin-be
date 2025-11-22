from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'location', 'website', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(read_only=True)
    created_events = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'is_verified', 
            'created_at', 'updated_at', 'profile', 'created_events'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified', 'created_events']
    
    def get_created_events(self, obj):
        """Return list of event IDs created by this user"""
        return list(obj.created_events.values_list('id', flat=True))
    



class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'date_of_birth', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        # Create user profile
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login - accepts email or username"""
    email_or_username = serializers.CharField(
        help_text="Enter your email address or username"
    )
    password = serializers.CharField(
        help_text="Enter your password"
    )
    
    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        
        if not email_or_username or not password:
            raise serializers.ValidationError('Both email/username and password are required')
        
        # Since USERNAME_FIELD is 'email', we need to handle this differently
        # First, try to find the user by username or email
        try:
            # Try to find user by username
            user = User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            try:
                # If username not found, try email
                user = User.objects.get(email=email_or_username)
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid email/username or password')
        
        # Now authenticate with the found user
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email/username or password')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value
