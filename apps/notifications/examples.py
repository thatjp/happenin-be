"""
Examples of how to integrate notifications with other apps in the Happin system.

This file demonstrates common use cases for sending notifications when certain events occur.
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .services import NotificationService
from .models import NotificationType, NotificationPriority

User = get_user_model()


def send_event_reminder_notification(event, user, hours_before=1):
    """
    Send a reminder notification for an upcoming event.
    
    Example usage:
        send_event_reminder_notification(event, user, hours_before=2)
    """
    # Calculate time until event
    event_start = timezone.make_aware(
        timezone.datetime.combine(event.start_date, event.open_time)
    )
    time_until = event_start - timezone.now()
    
    if time_until.total_seconds() <= 0:
        return None  # Event has already started
    
    # Format time for display
    if time_until.days > 0:
        time_display = f"{time_until.days} days"
    elif time_until.seconds > 3600:
        hours = time_until.seconds // 3600
        time_display = f"{hours} hours"
    else:
        minutes = time_until.seconds // 60
        time_display = f"{minutes} minutes"
    
    # Create context for template
    context = {
        'event_title': event.title,
        'time_until': time_display,
        'event_date': event.start_date.strftime('%B %d, %Y'),
        'event_time': event.open_time.strftime('%I:%M %p'),
        'event_location': event.full_address,
        'user_name': user.first_name or user.username
    }
    
    # Schedule notification to be sent at the right time
    scheduled_at = timezone.now() + timedelta(hours=hours_before)
    
    # Create notification using template
    notification = NotificationService.create_notification_from_template(
        recipient=user,
        template_name='Event Reminder',
        context=context,
        priority=NotificationPriority.HIGH,
        content_object=event,
        scheduled_at=scheduled_at
    )
    
    return notification


def send_event_update_notification(event, user, changes):
    """
    Send notification when an event is updated.
    
    Example usage:
        changes = {'title': 'Old Title → New Title', 'time': '2 PM → 3 PM'}
        send_event_update_notification(event, user, changes)
    """
    # Create context for template
    context = {
        'event_title': event.title,
        'user_name': user.first_name or user.username
    }
    
    # Create notification using template
    notification = NotificationService.create_notification_from_template(
        recipient=user,
        template_name='Event Update',
        context=context,
        priority=NotificationPriority.NORMAL,
        content_object=event
    )
    
    return notification


def send_event_cancellation_notification(event, user, reason=None):
    """
    Send notification when an event is cancelled.
    
    Example usage:
        send_event_cancellation_notification(event, user, reason="Weather conditions")
    """
    # Create context for template
    context = {
        'event_title': event.title,
        'user_name': user.first_name or user.username
    }
    
    # Create notification using template
    notification = NotificationService.create_notification_from_template(
        recipient=user,
        template_name='Event Cancellation',
        context=context,
        priority=NotificationPriority.HIGH,
        content_object=event
    )
    
    return notification


def send_new_event_nearby_notification(event, nearby_users, radius_miles=10):
    """
    Send notifications to users about new events near them.
    
    Example usage:
        nearby_users = get_users_within_radius(event.latitude, event.longitude, radius_miles)
        send_new_event_nearby_notification(event, nearby_users)
    """
    notifications = []
    
    for user in nearby_users:
        # Create context for template
        context = {
            'event_title': event.title,
            'user_name': user.first_name or user.username,
            'event_date': event.start_date.strftime('%B %d, %Y'),
            'event_time': event.open_time.strftime('%I:%M %p'),
            'event_location': event.full_address
        }
        
        # Create notification using template
        notification = NotificationService.create_notification_from_template(
            recipient=user,
            template_name='New Event Nearby',
            context=context,
            priority=NotificationPriority.NORMAL,
            content_object=event
        )
        
        if notification:
            notifications.append(notification)
    
    return notifications


def send_friend_request_notification(sender, recipient):
    """
    Send notification when a friend request is sent.
    
    Example usage:
        send_friend_request_notification(sender, recipient)
    """
    # Create context for template
    context = {
        'sender_name': sender.first_name or sender.username,
        'user_name': recipient.first_name or recipient.username
    }
    
    # Create notification using template
    notification = NotificationService.create_notification_from_template(
        recipient=recipient,
        template_name='Friend Invite',
        context=context,
        priority=NotificationPriority.NORMAL
    )
    
    return notification


def send_system_announcement_notification(users, title, message, priority=NotificationPriority.NORMAL):
    """
    Send system announcement to multiple users.
    
    Example usage:
        users = User.objects.filter(is_active=True)
        send_system_announcement_notification(users, "Maintenance Notice", "System will be down for maintenance")
    """
    notifications = []
    
    for user in users:
        # Create context for template
        context = {
            'title': title,
            'message': message,
            'user_name': user.first_name or user.username
        }
        
        # Create notification using template
        notification = NotificationService.create_notification_from_template(
            recipient=user,
            template_name='System Announcement',
            context=context,
            priority=priority
        )
        
        if notification:
            notifications.append(notification)
    
    return notifications


def send_bulk_notifications(users, notification_type, title, message, priority=NotificationPriority.NORMAL):
    """
    Send the same notification to multiple users efficiently.
    
    Example usage:
        users = User.objects.filter(location='New York')
        send_bulk_notifications(users, 'event_update', 'New York Events', 'Check out new events in your area!')
    """
    notifications = []
    
    for user in users:
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority
        )
        
        notifications.append(notification)
    
    return notifications


def send_scheduled_notification(user, notification_type, title, message, send_at, priority=NotificationPriority.NORMAL):
    """
    Send a notification at a specific time in the future.
    
    Example usage:
        send_at = timezone.now() + timedelta(days=1)
        send_scheduled_notification(user, 'event_reminder', 'Daily Digest', 'Here are today\'s events', send_at)
    """
    notification = NotificationService.create_notification(
        recipient=user,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        scheduled_at=send_at
    )
    
    return notification


# Example of integrating with Django signals
def setup_notification_signals():
    """
    Example of how to set up Django signals for automatic notifications.
    
    This would typically go in the app's apps.py or signals.py file.
    """
    from django.db.models.signals import post_save, post_delete
    from django.dispatch import receiver
    from apps.events.models import Event
    
    @receiver(post_save, sender=Event)
    def event_saved(sender, instance, created, **kwargs):
        """Send notifications when events are created or updated"""
        if created:
            # New event created - notify nearby users
            # This is a simplified example
            pass
        else:
            # Event updated - notify attendees
            # This is a simplified example
            pass
    
    @receiver(post_delete, sender=Event)
    def event_deleted(sender, instance, **kwargs):
        """Send notifications when events are deleted"""
        # Notify attendees that event was cancelled
        # This is a simplified example
        pass


# Example of a custom notification service
class EventNotificationService:
    """Custom service for event-related notifications"""
    
    @staticmethod
    def notify_event_attendees(event, notification_type, title, message, priority=NotificationPriority.NORMAL):
        """Send notification to all event attendees"""
        # This would get attendees from your event model
        # attendees = event.get_attendees()
        # return send_bulk_notifications(attendees, notification_type, title, message, priority)
        pass
    
    @staticmethod
    def notify_event_creator(event, notification_type, title, message, priority=NotificationPriority.NORMAL):
        """Send notification to event creator"""
        return NotificationService.create_notification(
            recipient=event.created_by,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            content_object=event
        )
    
    @staticmethod
    def send_event_reminders(event):
        """Send reminders to all event attendees"""
        # This would get attendees from your event model
        # attendees = event.get_attendees()
        # notifications = []
        # for attendee in attendees:
        #     notification = send_event_reminder_notification(event, attendee)
        #     if notification:
        #         notifications.append(notification)
        # return notifications
        pass
