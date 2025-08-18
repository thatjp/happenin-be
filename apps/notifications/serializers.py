from rest_framework import serializers
from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationPriority, NotificationStatus,
    NotificationChannel, NotificationLog
)
from django.utils import timezone


class NotificationTypeSerializer(serializers.Serializer):
    """Serializer for notification types"""
    value = serializers.CharField()
    display_name = serializers.CharField(source='label')


class NotificationPrioritySerializer(serializers.Serializer):
    """Serializer for notification priorities"""
    value = serializers.CharField()
    display_name = serializers.CharField(source='label')


class NotificationStatusSerializer(serializers.Serializer):
    """Serializer for notification statuses"""
    value = serializers.CharField()
    display_name = serializers.CharField(source='label')


class NotificationChannelSerializer(serializers.Serializer):
    """Serializer for notification channels"""
    value = serializers.CharField()
    display_name = serializers.CharField(source='label')


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'notification_type_display',
            'title_template', 'message_template', 'email_subject_template',
            'email_body_template', 'sms_template', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )

    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification preferences"""
    class Meta:
        model = NotificationPreference
        fields = ['in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs"""
    channel_display = serializers.CharField(
        source='get_channel_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'channel', 'channel_display', 'status', 'status_display',
            'attempt_count', 'error_message', 'sent_at'
        ]
        read_only_fields = ['id', 'sent_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    is_read = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    
    # Related object information
    content_type_name = serializers.CharField(
        source='content_type.model',
        read_only=True
    )
    
    # User information
    recipient_username = serializers.CharField(
        source='recipient.username',
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_username', 'notification_type',
            'notification_type_display', 'title', 'message', 'content_type',
            'object_id', 'content_type_name', 'priority', 'priority_display',
            'status', 'status_display', 'channels', 'scheduled_at', 'sent_at',
            'read_at', 'metadata', 'is_read', 'is_pending', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'recipient', 'created_at', 'updated_at', 'is_read', 'is_pending'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    class Meta:
        model = Notification
        fields = [
            'recipient', 'notification_type', 'title', 'message',
            'content_type', 'object_id', 'priority', 'scheduled_at', 'metadata'
        ]

    def validate(self, attrs):
        """Validate notification data"""
        # Check if content_type and object_id are both provided or both missing
        content_type = attrs.get('content_type')
        object_id = attrs.get('object_id')
        
        if bool(content_type) != bool(object_id):
            raise serializers.ValidationError(
                "Both content_type and object_id must be provided together"
            )
        
        # Validate scheduled_at is in the future if provided
        scheduled_at = attrs.get('scheduled_at')
        if scheduled_at and scheduled_at <= timezone.now():
            raise serializers.ValidationError(
                "Scheduled time must be in the future"
            )
        
        return attrs


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notifications"""
    class Meta:
        model = Notification
        fields = ['title', 'message', 'priority', 'scheduled_at', 'metadata']


class NotificationBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating notifications"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of notification IDs to update"
    )
    action = serializers.ChoiceField(
        choices=['mark_read', 'mark_unread', 'delete'],
        help_text="Action to perform on selected notifications"
    )

    def validate_notification_ids(self, value):
        """Validate notification IDs"""
        if not value:
            raise serializers.ValidationError("Notification IDs list cannot be empty")
        if len(value) > 100:  # Limit bulk operations
            raise serializers.ValidationError("Cannot update more than 100 notifications at once")
        return value


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total_notifications = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    sent_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    
    # Counts by type
    by_type = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Count of notifications by type"
    )
    
    # Counts by priority
    by_priority = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Count of notifications by priority"
    )


class NotificationTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notification templates"""
    class Meta:
        model = NotificationTemplate
        fields = [
            'name', 'notification_type', 'title_template', 'message_template',
            'email_subject_template', 'email_body_template', 'sms_template'
        ]

    def validate(self, attrs):
        """Validate template data"""
        notification_type = attrs.get('notification_type')
        name = attrs.get('name')
        
        # Check if template name is unique for the notification type
        if NotificationTemplate.objects.filter(
            notification_type=notification_type,
            name=name
        ).exists():
            raise serializers.ValidationError(
                f"A template with name '{name}' already exists for this notification type"
            )
        
        return attrs


class NotificationTemplateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification templates"""
    class Meta:
        model = NotificationTemplate
        fields = [
            'title_template', 'message_template', 'email_subject_template',
            'email_body_template', 'sms_template', 'is_active'
        ]
