from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class NotificationType(models.TextChoices):
    """Types of notifications that can be sent"""
    EVENT_REMINDER = 'event_reminder', _('Event Reminder')
    EVENT_UPDATE = 'event_update', _('Event Update')
    EVENT_CANCELLATION = 'event_cancellation', _('Event Cancellation')
    NEW_EVENT_NEARBY = 'new_event_nearby', _('New Event Nearby')
    FRIEND_INVITE = 'friend_invite', _('Friend Invite')
    FRIEND_ACCEPTED = 'friend_accepted', _('Friend Accepted')
    EVENT_INVITE = 'event_invite', _('Event Invite')
    EVENT_RSVP = 'event_rsvp', _('Event RSVP')
    SYSTEM_ANNOUNCEMENT = 'system_announcement', _('System Announcement')
    ACCOUNT_VERIFICATION = 'account_verification', _('Account Verification')
    PASSWORD_RESET = 'password_reset', _('Password Reset')
    SECURITY_ALERT = 'security_alert', _('Security Alert')


class NotificationPriority(models.TextChoices):
    """Priority levels for notifications"""
    LOW = 'low', _('Low')
    NORMAL = 'normal', _('Normal')
    HIGH = 'high', _('High')
    URGENT = 'urgent', _('Urgent')


class NotificationStatus(models.TextChoices):
    """Status of notifications"""
    PENDING = 'pending', _('Pending')
    SENT = 'sent', _('Sent')
    DELIVERED = 'delivered', _('Delivered')
    READ = 'read', _('Read')
    FAILED = 'failed', _('Failed')


class NotificationChannel(models.TextChoices):
    """Channels through which notifications can be sent"""
    IN_APP = 'in_app', _('In-App')
    EMAIL = 'email', _('Email')
    SMS = 'sms', _('SMS')
    PUSH = 'push', _('Push Notification')


class NotificationTemplate(models.Model):
    """Template for different types of notifications"""
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        help_text=_("Type of notification this template is for")
    )
    title_template = models.CharField(
        max_length=200,
        help_text=_("Template for notification title with placeholders")
    )
    message_template = models.TextField(
        help_text=_("Template for notification message with placeholders")
    )
    email_subject_template = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Template for email subject line")
    )
    email_body_template = models.TextField(
        blank=True,
        help_text=_("Template for email body")
    )
    sms_template = models.CharField(
        max_length=160,
        blank=True,
        help_text=_("Template for SMS messages")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')

    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"


class NotificationPreference(models.Model):
    """User preferences for different types of notifications"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    in_app_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'notification_type']
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"


class Notification(models.Model):
    """Main notification model"""
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Generic foreign key to link to related objects (events, users, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Notification metadata
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )
    
    # Channel-specific data
    channels = models.JSONField(
        default=list,
        help_text=_("List of channels this notification was sent through")
    )
    
    # Timing
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional data for the notification")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['recipient', 'created_at']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['scheduled_at', 'status']),
        ]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    @property
    def is_read(self):
        """Check if notification has been read"""
        return self.status == NotificationStatus.READ

    @property
    def is_pending(self):
        """Check if notification is pending to be sent"""
        return self.status == NotificationStatus.PENDING

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.status = NotificationStatus.READ
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at', 'updated_at'])

    def mark_as_sent(self, channel=None):
        """Mark notification as sent through a specific channel"""
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        if channel and channel not in self.channels:
            self.channels.append(channel)
        self.save(update_fields=['status', 'sent_at', 'channels', 'updated_at'])

    def mark_as_delivered(self, channel=None):
        """Mark notification as delivered through a specific channel"""
        self.status = NotificationStatus.DELIVERED
        if channel and channel not in self.channels:
            self.channels.append(channel)
        self.save(update_fields=['status', 'channels', 'updated_at'])

    def mark_as_failed(self, channel=None):
        """Mark notification as failed through a specific channel"""
        self.status = NotificationStatus.FAILED
        if channel and channel not in self.channels:
            self.channels.append(channel)
        self.save(update_fields=['status', 'channels', 'updated_at'])


class NotificationLog(models.Model):
    """Log of notification delivery attempts"""
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs'
    )
    channel = models.CharField(max_length=20, choices=NotificationChannel.choices)
    status = models.CharField(max_length=20, choices=NotificationStatus.choices)
    attempt_count = models.PositiveIntegerField(default=1)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = _('Notification Log')
        verbose_name_plural = _('Notification Logs')

    def __str__(self):
        return f"{self.notification.title} - {self.channel} - {self.status}"
