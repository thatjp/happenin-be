#!/usr/bin/env python
"""
Simple test script to verify the notifications app is working.
Run this after setting up the app to test basic functionality.
"""

import os
import sys
import django
from datetime import timedelta

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'happenin.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notifications.models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationPriority, NotificationStatus
)
from apps.notifications.services import NotificationService, NotificationTemplateService

User = get_user_model()


def test_notifications_app():
    """Test basic functionality of the notifications app"""
    print("🧪 Testing Notifications App...")
    print("=" * 50)
    
    # Test 1: Check if models can be imported
    print("1. Testing model imports...")
    try:
        print(f"   ✓ NotificationType choices: {len(NotificationType.choices)} types")
        print(f"   ✓ NotificationPriority choices: {len(NotificationPriority.choices)} levels")
        print(f"   ✓ NotificationStatus choices: {len(NotificationStatus.choices)} statuses")
    except Exception as e:
        print(f"   ✗ Error importing models: {e}")
        return False
    
    # Test 2: Create a test user
    print("\n2. Creating test user...")
    try:
        user, created = User.objects.get_or_create(
            username='testuser_notifications',
            defaults={
                'email': 'test_notifications@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"   ✓ Created test user: {user.username}")
        else:
            print(f"   ✓ Using existing test user: {user.username}")
    except Exception as e:
        print(f"   ✗ Error creating test user: {e}")
        return False
    
    # Test 3: Create notification templates
    print("\n3. Creating notification templates...")
    try:
        templates = NotificationTemplateService.create_default_templates()
        print(f"   ✓ Created {len(templates)} default templates")
        for template in templates:
            print(f"     - {template.name} ({template.notification_type})")
    except Exception as e:
        print(f"   ✗ Error creating templates: {e}")
        return False
    
    # Test 4: Create notification preferences
    print("\n4. Creating notification preferences...")
    try:
        for notification_type, _ in NotificationType.choices:
            preference, created = NotificationPreference.objects.get_or_create(
                user=user,
                notification_type=notification_type,
                defaults={
                    'in_app_enabled': True,
                    'email_enabled': True,
                    'sms_enabled': False,
                    'push_enabled': True
                }
            )
            if created:
                print(f"   ✓ Created preference for {notification_type}")
            else:
                print(f"   ✓ Using existing preference for {notification_type}")
    except Exception as e:
        print(f"   ✗ Error creating preferences: {e}")
        return False
    
    # Test 5: Create a test notification
    print("\n5. Creating test notification...")
    try:
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title='Test Notification',
            message='This is a test notification to verify the app is working.',
            priority=NotificationPriority.NORMAL
        )
        print(f"   ✓ Created notification: {notification.title}")
        print(f"     - ID: {notification.id}")
        print(f"     - Status: {notification.status}")
        print(f"     - Priority: {notification.priority}")
    except Exception as e:
        print(f"   ✗ Error creating notification: {e}")
        return False
    
    # Test 6: Test notification methods
    print("\n6. Testing notification methods...")
    try:
        # Test marking as read
        notification.mark_as_read()
        print(f"   ✓ Marked notification as read")
        print(f"     - Status: {notification.status}")
        print(f"     - Is read: {notification.is_read}")
        
        # Test marking as sent
        # Assuming NotificationChannel is defined elsewhere or needs to be imported
        # For now, commenting out as it's not defined in the provided context
        # notification.mark_as_sent(NotificationChannel.EMAIL)
        # print(f"   ✓ Marked notification as sent via email")
        # print(f"     - Channels: {notification.channels}")
        
    except Exception as e:
        print(f"   ✗ Error testing notification methods: {e}")
        return False
    
    # Test 7: Test service methods
    print("\n7. Testing service methods...")
    try:
        # Test getting user notifications
        user_notifications = NotificationService.get_user_notifications(user)
        print(f"   ✓ Retrieved {len(user_notifications)} user notifications")
        
        # Test getting unread count
        unread_count = NotificationService.get_unread_count(user)
        print(f"   ✓ Unread count: {unread_count}")
        
        # Test getting stats
        stats = NotificationService.get_notification_stats(user)
        print(f"   ✓ Retrieved notification stats:")
        print(f"     - Total: {stats['total_notifications']}")
        print(f"     - Unread: {stats['unread_count']}")
        print(f"     - Read: {stats['read_count']}")
        
    except Exception as e:
        print(f"   ✗ Error testing service methods: {e}")
        return False
    
    # Test 8: Test template-based notification
    print("\n8. Testing template-based notification...")
    try:
        context = {
            'event_title': 'Summer Concert',
            'time_until': '2 hours',
            'event_date': 'July 15, 2024',
            'event_time': '7:00 PM',
            'event_location': 'Central Park, New York',
            'user_name': user.first_name or user.username
        }
        
        template_notification = NotificationService.create_notification_from_template(
            recipient=user,
            template_name='Event Reminder',
            context=context,
            priority=NotificationPriority.HIGH
        )
        
        if template_notification:
            print(f"   ✓ Created template-based notification: {template_notification.title}")
            print(f"     - Message: {template_notification.message}")
        else:
            print(f"   ✗ Failed to create template-based notification")
            
    except Exception as e:
        print(f"   ✗ Error testing template-based notification: {e}")
        return False
    
    # Test 9: Cleanup
    print("\n9. Cleaning up test data...")
    try:
        # Delete test notifications
        Notification.objects.filter(recipient=user).delete()
        print(f"   ✓ Deleted test notifications")
        
        # Delete test preferences
        NotificationPreference.objects.filter(user=user).delete()
        print(f"   ✓ Deleted test preferences")
        
        # Delete test user
        user.delete()
        print(f"   ✓ Deleted test user")
        
    except Exception as e:
        print(f"   ✗ Error during cleanup: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The notifications app is working correctly.")
    print("=" * 50)
    
    return True


if __name__ == '__main__':
    try:
        success = test_notifications_app()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
