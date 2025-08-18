from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationLog, NotificationType, NotificationPriority,
    NotificationStatus, NotificationChannel
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for notification templates"""
    list_display = ['name', 'notification_type', 'is_active', 'created_at']
    list_filter = ['notification_type', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'notification_type', 'is_active')
        }),
        ('Templates', {
            'fields': ('title_template', 'message_template')
        }),
        ('Email Templates', {
            'fields': ('email_subject_template', 'email_body_template'),
            'classes': ('collapse',)
        }),
        ('SMS Template', {
            'fields': ('sms_template',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for notification preferences"""
    list_display = ['user', 'notification_type', 'in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled']
    list_filter = ['notification_type', 'in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__username', 'notification_type']
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'notification_type')
        }),
        ('Channel Preferences', {
            'fields': ('in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for notifications"""
    list_display = [
        'id', 'recipient', 'notification_type', 'title', 'priority', 
        'status', 'is_read_display', 'created_at'
    ]
    list_filter = [
        'notification_type', 'priority', 'status', 'created_at', 'scheduled_at'
    ]
    search_fields = ['recipient__username', 'recipient__email', 'title', 'message']
    readonly_fields = [
        'created_at', 'updated_at', 'sent_at', 'read_at', 'is_read_display'
    ]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recipient', 'notification_type', 'title', 'message')
        }),
        ('Content Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('priority', 'status', 'channels', 'metadata')
        }),
        ('Timing', {
            'fields': ('scheduled_at', 'sent_at', 'read_at')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at', 'is_read_display'),
            'classes': ('collapse',)
        })
    )
    
    def is_read_display(self, obj):
        """Display whether notification is read"""
        if obj.is_read:
            return format_html('<span style="color: green;">✓ Read</span>')
        else:
            return format_html('<span style="color: red;">✗ Unread</span>')
    is_read_display.short_description = 'Read Status'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('recipient', 'content_type')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin interface for notification logs"""
    list_display = ['notification', 'channel', 'status', 'attempt_count', 'sent_at']
    list_filter = ['channel', 'status', 'sent_at']
    search_fields = ['notification__title', 'error_message']
    readonly_fields = ['sent_at']
    ordering = ['-sent_at']
    
    fieldsets = (
        ('Notification', {
            'fields': ('notification',)
        }),
        ('Delivery Info', {
            'fields': ('channel', 'status', 'attempt_count')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('sent_at',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('notification')


# Note: Choice models (NotificationType, NotificationPriority, NotificationStatus, NotificationChannel)
# are not Django models, so they cannot be registered in the admin interface.
# They are defined as TextChoices in the models.py file.
