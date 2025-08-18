from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from typing import Optional, Dict, Any, List
from datetime import timedelta

from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationPriority, NotificationStatus,
    NotificationChannel
)

User = get_user_model()


class NotificationService:
    """Service class for notification operations"""
    
    @staticmethod
    def create_notification(
        recipient: User,
        notification_type: str,
        title: str,
        message: str,
        priority: str = NotificationPriority.NORMAL,
        content_object: Optional[Any] = None,
        scheduled_at: Optional[timezone.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            recipient: User to receive the notification
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            content_object: Related object (optional)
            scheduled_at: When to send (optional)
            metadata: Additional data (optional)
        
        Returns:
            Created notification instance
        """
        notification_data = {
            'recipient': recipient,
            'notification_type': notification_type,
            'title': title,
            'message': message,
            'priority': priority,
            'scheduled_at': scheduled_at,
            'metadata': metadata or {}
        }
        
        # Add content object if provided
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            notification_data['content_type'] = content_type
            notification_data['object_id'] = content_object.id
        
        notification = Notification.objects.create(**notification_data)
        return notification
    
    @staticmethod
    def create_notification_from_template(
        recipient: User,
        template_name: str,
        context: Dict[str, Any],
        priority: str = NotificationPriority.NORMAL,
        content_object: Optional[Any] = None,
        scheduled_at: Optional[timezone.datetime] = None
    ) -> Optional[Notification]:
        """
        Create notification using a template
        
        Args:
            recipient: User to receive the notification
            template_name: Name of the template to use
            context: Context data for template formatting
            priority: Priority level
            content_object: Related object (optional)
            scheduled_at: When to send (optional)
        
        Returns:
            Created notification instance or None if template not found
        """
        try:
            template = NotificationTemplate.objects.get(
                name=template_name,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return None
        
        # Format templates with context
        title = template.title_template.format(**context)
        message = template.message_template.format(**context)
        
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=template.notification_type,
            title=title,
            message=message,
            priority=priority,
            content_object=content_object,
            scheduled_at=scheduled_at
        )
    
    @staticmethod
    def send_notification(
        notification: Notification,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send notification through specified channels
        
        Args:
            notification: Notification instance to send
            channels: List of channels to use (defaults to user preferences)
        
        Returns:
            Dictionary mapping channels to success status
        """
        if channels is None:
            # Get user preferences for this notification type
            try:
                preference = NotificationPreference.objects.get(
                    user=notification.recipient,
                    notification_type=notification.notification_type
                )
                channels = []
                if preference.in_app_enabled:
                    channels.append(NotificationChannel.IN_APP)
                if preference.email_enabled:
                    channels.append(NotificationChannel.EMAIL)
                if preference.sms_enabled:
                    channels.append(NotificationChannel.SMS)
                if preference.push_enabled:
                    channels.append(NotificationChannel.PUSH)
            except NotificationPreference.DoesNotExist:
                # Use default channels if no preference set
                channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL]
        
        results = {}
        
        for channel in channels:
            try:
                success = NotificationService._send_through_channel(notification, channel)
                results[channel] = success
                
                if success:
                    notification.mark_as_sent(channel)
                else:
                    notification.mark_as_failed(channel)
                    
            except Exception as e:
                results[channel] = False
                notification.mark_as_failed(channel)
        
        return results
    
    @staticmethod
    def _send_through_channel(notification: Notification, channel: str) -> bool:
        """
        Send notification through a specific channel
        
        Args:
            notification: Notification to send
            channel: Channel to use
        
        Returns:
            True if successful, False otherwise
        """
        # This is a placeholder implementation
        # In a real application, you would integrate with actual services
        
        if channel == NotificationChannel.IN_APP:
            # In-app notifications are always "sent" immediately
            return True
            
        elif channel == NotificationChannel.EMAIL:
            # TODO: Integrate with email service (SendGrid, AWS SES, etc.)
            # For now, just simulate success
            return True
            
        elif channel == NotificationChannel.SMS:
            # TODO: Integrate with SMS service (Twilio, AWS SNS, etc.)
            # For now, just simulate success
            return True
            
        elif channel == NotificationChannel.PUSH:
            # TODO: Integrate with push notification service (Firebase, etc.)
            # For now, just simulate success
            return True
        
        return False
    
    @staticmethod
    def get_user_notifications(
        user: User,
        status: Optional[str] = None,
        notification_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Notification]:
        """
        Get notifications for a user with optional filtering
        
        Args:
            user: User to get notifications for
            status: Filter by status
            notification_type: Filter by type
            limit: Maximum number of notifications to return
        
        Returns:
            List of notifications
        """
        queryset = Notification.objects.filter(recipient=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if limit:
            queryset = queryset[:limit]
        
        return list(queryset)
    
    @staticmethod
    def mark_notifications_read(
        user: User,
        notification_ids: Optional[List[int]] = None
    ) -> int:
        """
        Mark notifications as read
        
        Args:
            user: User whose notifications to mark
            notification_ids: Specific notification IDs (if None, mark all)
        
        Returns:
            Number of notifications marked as read
        """
        queryset = Notification.objects.filter(recipient=user)
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        # Only mark unread notifications
        queryset = queryset.filter(
            status__in=[
                NotificationStatus.PENDING,
                NotificationStatus.SENT,
                NotificationStatus.DELIVERED
            ]
        )
        
        count = queryset.count()
        queryset.update(
            status=NotificationStatus.READ,
            read_at=timezone.now()
        )
        
        return count
    
    @staticmethod
    def get_unread_count(user: User) -> int:
        """
        Get count of unread notifications for a user
        
        Args:
            user: User to get count for
        
        Returns:
            Number of unread notifications
        """
        return Notification.objects.filter(
            recipient=user,
            status__in=[
                NotificationStatus.PENDING,
                NotificationStatus.SENT,
                NotificationStatus.DELIVERED
            ]
        ).count()
    
    @staticmethod
    def cleanup_old_notifications(days_old: int = 90) -> int:
        """
        Clean up old read notifications
        
        Args:
            days_old: Age threshold in days
        
        Returns:
            Number of notifications deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Delete old read notifications
        old_notifications = Notification.objects.filter(
            status=NotificationStatus.READ,
            read_at__lt=cutoff_date
        )
        
        count = old_notifications.count()
        old_notifications.delete()
        
        return count
    
    @staticmethod
    def get_notification_stats(user: User) -> Dict[str, Any]:
        """
        Get notification statistics for a user
        
        Args:
            user: User to get stats for
        
        Returns:
            Dictionary with notification statistics
        """
        notifications = Notification.objects.filter(recipient=user)
        
        stats = {
            'total_notifications': notifications.count(),
            'unread_count': NotificationService.get_unread_count(user),
            'pending_count': notifications.filter(status=NotificationStatus.PENDING).count(),
            'sent_count': notifications.filter(status=NotificationStatus.SENT).count(),
            'delivered_count': notifications.filter(status=NotificationStatus.DELIVERED).count(),
            'read_count': notifications.filter(status=NotificationStatus.READ).count(),
            'failed_count': notifications.filter(status=NotificationStatus.FAILED).count(),
            'by_type': {},
            'by_priority': {}
        }
        
        # Count by type
        for notification_type, _ in NotificationType.choices:
            stats['by_type'][notification_type] = notifications.filter(
                notification_type=notification_type
            ).count()
        
        # Count by priority
        for priority, _ in NotificationPriority.choices:
            stats['by_priority'][priority] = notifications.filter(
                priority=priority
            ).count()
        
        return stats


class NotificationTemplateService:
    """Service class for notification template operations"""
    
    @staticmethod
    def create_default_templates() -> List[NotificationTemplate]:
        """
        Create default notification templates
        
        Returns:
            List of created templates
        """
        default_templates = [
            {
                'name': 'Event Reminder',
                'notification_type': NotificationType.EVENT_REMINDER,
                'title_template': 'Event Reminder: {event_title}',
                'message_template': 'Your event "{event_title}" starts in {time_until}. Don\'t forget to attend!',
                'email_subject_template': 'Event Reminder: {event_title}',
                'email_body_template': 'Hi {user_name},\n\nYour event "{event_title}" starts in {time_until}.\n\nEvent Details:\n- Date: {event_date}\n- Time: {event_time}\n- Location: {event_location}\n\nDon\'t forget to attend!\n\nBest regards,\nThe Happin Team',
                'sms_template': 'Reminder: {event_title} starts in {time_until}. Location: {event_location}'
            },
            {
                'name': 'Event Update',
                'notification_type': NotificationType.EVENT_UPDATE,
                'title_template': 'Event Updated: {event_title}',
                'message_template': 'The event "{event_title}" has been updated. Check the details for changes.',
                'email_subject_template': 'Event Updated: {event_title}',
                'email_body_template': 'Hi {user_name},\n\nThe event "{event_title}" has been updated.\n\nPlease check the event details for any changes.\n\nBest regards,\nThe Happin Team',
                'sms_template': 'Event "{event_title}" has been updated. Check details for changes.'
            },
            {
                'name': 'Event Cancellation',
                'notification_type': NotificationType.EVENT_CANCELLATION,
                'title_template': 'Event Cancelled: {event_title}',
                'message_template': 'The event "{event_title}" has been cancelled. We apologize for any inconvenience.',
                'email_subject_template': 'Event Cancelled: {event_title}',
                'email_body_template': 'Hi {user_name},\n\nWe regret to inform you that the event "{event_title}" has been cancelled.\n\nWe apologize for any inconvenience this may cause.\n\nBest regards,\nThe Happin Team',
                'sms_template': 'Event "{event_title}" has been cancelled. We apologize for any inconvenience.'
            },
            {
                'name': 'New Event Nearby',
                'notification_type': NotificationType.NEW_EVENT_NEARBY,
                'title_template': 'New Event Nearby: {event_title}',
                'message_template': 'A new event "{event_title}" has been created near you. Check it out!',
                'email_subject_template': 'New Event Nearby: {event_title}',
                'email_body_template': 'Hi {user_name},\n\nA new event "{event_title}" has been created near your location.\n\nEvent Details:\n- Date: {event_date}\n- Time: {event_time}\n- Location: {event_location}\n\nCheck it out and see if you\'d like to attend!\n\nBest regards,\nThe Happin Team',
                'sms_template': 'New event "{event_title}" nearby! Date: {event_date}, Location: {event_location}'
            },
            {
                'name': 'Friend Invite',
                'notification_type': NotificationType.FRIEND_INVITE,
                'title_template': 'Friend Request from {sender_name}',
                'message_template': '{sender_name} has sent you a friend request. Accept or decline?',
                'email_subject_template': 'Friend Request from {sender_name}',
                'email_body_template': 'Hi {user_name},\n\n{sender_name} has sent you a friend request on Happin.\n\nTo accept or decline this request, please log in to your account.\n\nBest regards,\nThe Happin Team',
                'sms_template': 'Friend request from {sender_name}. Log in to accept or decline.'
            },
            {
                'name': 'System Announcement',
                'notification_type': NotificationType.SYSTEM_ANNOUNCEMENT,
                'title_template': 'System Announcement: {title}',
                'message_template': '{message}',
                'email_subject_template': 'System Announcement: {title}',
                'email_body_template': 'Hi {user_name},\n\n{message}\n\nBest regards,\nThe Happin Team',
                'sms_template': 'System: {title} - {message}'
            }
        ]
        
        created_templates = []
        
        for template_data in default_templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_templates.append(template)
        
        return created_templates
