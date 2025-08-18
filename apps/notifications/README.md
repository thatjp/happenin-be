# Notifications App

A comprehensive Django app for managing user notifications in the Happin backend system.

## Features

- **Multi-channel notifications**: Support for in-app, email, SMS, and push notifications
- **Template system**: Reusable notification templates with placeholder support
- **User preferences**: Granular control over notification types and channels
- **Priority levels**: Configurable notification priorities (low, normal, high, urgent)
- **Status tracking**: Full lifecycle tracking from pending to delivered/read
- **Bulk operations**: Efficient bulk marking of notifications as read/unread
- **Statistics**: Comprehensive notification analytics and reporting
- **Admin interface**: Full Django admin integration for management

## Models

### Core Models

- **Notification**: Main notification entity with recipient, content, and metadata
- **NotificationTemplate**: Reusable templates for different notification types
- **NotificationPreference**: User preferences for notification types and channels
- **NotificationLog**: Audit trail for notification delivery attempts

### Choice Models

- **NotificationType**: Predefined notification categories (event reminders, updates, etc.)
- **NotificationPriority**: Priority levels (low, normal, high, urgent)
- **NotificationStatus**: Status tracking (pending, sent, delivered, read, failed)
- **NotificationChannel**: Delivery channels (in-app, email, SMS, push)

## API Endpoints

### Notifications

- `GET /api/notifications/notifications/` - List user notifications
- `POST /api/notifications/notifications/` - Create new notification
- `GET /api/notifications/notifications/{id}/` - Get notification details
- `PUT /api/notifications/notifications/{id}/` - Update notification
- `DELETE /api/notifications/notifications/{id}/` - Delete notification
- `POST /api/notifications/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/notifications/{id}/mark_unread/` - Mark as unread
- `POST /api/notifications/notifications/mark_all_read/` - Mark all as read
- `POST /api/notifications/notifications/bulk_update/` - Bulk operations
- `GET /api/notifications/notifications/unread/` - Get unread count
- `GET /api/notifications/notifications/stats/` - Get statistics

### Templates

- `GET /api/notifications/templates/` - List notification templates
- `POST /api/notifications/templates/` - Create new template
- `GET /api/notifications/templates/{id}/` - Get template details
- `PUT /api/notifications/templates/{id}/` - Update template
- `DELETE /api/notifications/templates/{id}/` - Delete template
- `GET /api/notifications/templates/by_type/` - Get templates by type

### Preferences

- `GET /api/notifications/preferences/` - List user preferences
- `POST /api/notifications/preferences/` - Create preference
- `PUT /api/notifications/preferences/{id}/` - Update preference
- `DELETE /api/notifications/preferences/{id}/` - Delete preference
- `GET /api/notifications/preferences/summary/` - Get preferences summary
- `POST /api/notifications/preferences/bulk_update/` - Bulk update preferences

### Logs

- `GET /api/notifications/logs/` - List delivery logs
- `GET /api/notifications/logs/{id}/` - Get log details

### Choices

- `GET /api/notifications/types/` - List notification types
- `GET /api/notifications/priorities/` - List priority levels
- `GET /api/notifications/statuses/` - List status options
- `GET /api/notifications/channels/` - List delivery channels

## Usage Examples

### Creating a Notification

```python
from apps.notifications.models import Notification, NotificationType, NotificationPriority

# Create a simple notification
notification = Notification.objects.create(
    recipient=user,
    notification_type=NotificationType.EVENT_REMINDER,
    title="Event Reminder",
    message="Your event starts in 1 hour",
    priority=NotificationPriority.HIGH
)
```

### Using Templates

```python
from apps.notifications.models import NotificationTemplate

# Get template and format with context
template = NotificationTemplate.objects.get(name='Event Reminder Template')
title = template.title_template.format(event_title="Summer Concert")
message = template.message_template.format(
    event_title="Summer Concert",
    time_until="2 hours"
)

notification = Notification.objects.create(
    recipient=user,
    notification_type=template.notification_type,
    title=title,
    message=message
)
```

### Managing User Preferences

```python
from apps.notifications.models import NotificationPreference

# Create or update user preference
preference, created = NotificationPreference.objects.get_or_create(
    user=user,
    notification_type=NotificationType.EVENT_REMINDER,
    defaults={
        'in_app_enabled': True,
        'email_enabled': True,
        'sms_enabled': False,
        'push_enabled': True
    }
)

# Update existing preference
if not created:
    preference.sms_enabled = True
    preference.save()
```

### Bulk Operations

```python
# Mark multiple notifications as read
notification_ids = [1, 2, 3, 4]
notifications = Notification.objects.filter(id__in=notification_ids)
notifications.update(
    status=NotificationStatus.READ,
    read_at=timezone.now()
)
```

## Configuration

### Settings

Add the notifications app to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'apps.notifications',
]
```

### URLs

Include the notification URLs in your main URL configuration:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('api/notifications/', include('apps.notifications.urls')),
]
```

## Admin Interface

The app provides a comprehensive Django admin interface for:

- Managing notification templates
- Viewing and managing user preferences
- Monitoring notification delivery
- Analyzing notification logs
- Managing notification types, priorities, statuses, and channels

## Testing

Run the test suite:

```bash
python manage.py test apps.notifications
```

The test suite covers:

- Model creation and validation
- API endpoint functionality
- Bulk operations
- User preference management
- Template system
- Choice models

## Future Enhancements

- **Real-time notifications**: WebSocket support for instant delivery
- **Scheduled notifications**: Cron-based scheduling system
- **Advanced templating**: Jinja2 template engine support
- **Rate limiting**: Prevent notification spam
- **A/B testing**: Test different notification formats
- **Analytics dashboard**: Advanced reporting and insights
- **Mobile push**: Firebase/APNS integration
- **Email templates**: HTML email support with responsive design

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting

## License

This app is part of the Happin backend system and follows the same licensing terms.
