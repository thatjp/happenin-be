from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from datetime import timedelta

from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationPriority, NotificationStatus,
    NotificationChannel, NotificationLog
)

User = get_user_model()


class NotificationModelTest(TestCase):
    """Test cases for Notification model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.EVENT_REMINDER,
            title='Test Notification',
            message='This is a test notification',
            priority=NotificationPriority.NORMAL
        )
    
    def test_notification_creation(self):
        """Test notification creation"""
        self.assertEqual(self.notification.recipient, self.user)
        self.assertEqual(self.notification.notification_type, NotificationType.EVENT_REMINDER)
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.status, NotificationStatus.PENDING)
        self.assertFalse(self.notification.is_read)
        self.assertTrue(self.notification.is_pending)
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        self.notification.mark_as_read()
        self.assertEqual(self.notification.status, NotificationStatus.READ)
        self.assertTrue(self.notification.is_read)
        self.assertIsNotNone(self.notification.read_at)
    
    def test_mark_as_sent(self):
        """Test marking notification as sent"""
        self.notification.mark_as_sent(NotificationChannel.EMAIL)
        self.assertEqual(self.notification.status, NotificationStatus.SENT)
        self.assertIsNotNone(self.notification.sent_at)
        self.assertIn(NotificationChannel.EMAIL, self.notification.channels)
    
    def test_mark_as_delivered(self):
        """Test marking notification as delivered"""
        self.notification.mark_as_delivered(NotificationChannel.IN_APP)
        self.assertEqual(self.notification.status, NotificationStatus.DELIVERED)
        self.assertIn(NotificationChannel.IN_APP, self.notification.channels)
    
    def test_mark_as_failed(self):
        """Test marking notification as failed"""
        self.notification.mark_as_failed(NotificationChannel.SMS)
        self.assertEqual(self.notification.status, NotificationStatus.FAILED)
        self.assertIn(NotificationChannel.SMS, self.notification.channels)
    
    def test_string_representation(self):
        """Test string representation of notification"""
        expected = f"{self.user.username} - Test Notification"
        self.assertEqual(str(self.notification), expected)


class NotificationTemplateModelTest(TestCase):
    """Test cases for NotificationTemplate model"""
    
    def setUp(self):
        """Set up test data"""
        self.template = NotificationTemplate.objects.create(
            name='Event Reminder Template',
            notification_type=NotificationType.EVENT_REMINDER,
            title_template='Reminder: {event_title}',
            message_template='Your event {event_title} starts in {time_until}',
            email_subject_template='Event Reminder: {event_title}',
            email_body_template='Don\'t forget about your event {event_title}!'
        )
    
    def test_template_creation(self):
        """Test template creation"""
        self.assertEqual(self.template.name, 'Event Reminder Template')
        self.assertEqual(self.template.notification_type, NotificationType.EVENT_REMINDER)
        self.assertTrue(self.template.is_active)
    
    def test_string_representation(self):
        """Test string representation of template"""
        expected = "Event Reminder Template (Event Reminder)"
        self.assertEqual(str(self.template), expected)


class NotificationPreferenceModelTest(TestCase):
    """Test cases for NotificationPreference model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            notification_type=NotificationType.EVENT_REMINDER,
            in_app_enabled=True,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True
        )
    
    def test_preference_creation(self):
        """Test preference creation"""
        self.assertEqual(self.preference.user, self.user)
        self.assertEqual(self.preference.notification_type, NotificationType.EVENT_REMINDER)
        self.assertTrue(self.preference.in_app_enabled)
        self.assertTrue(self.preference.email_enabled)
        self.assertFalse(self.preference.sms_enabled)
        self.assertTrue(self.preference.push_enabled)
    
    def test_string_representation(self):
        """Test string representation of preference"""
        expected = f"{self.user.username} - Event Reminder"
        self.assertEqual(str(self.preference), expected)


class NotificationLogModelTest(TestCase):
    """Test cases for NotificationLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.EVENT_REMINDER,
            title='Test Notification',
            message='This is a test notification'
        )
        
        self.log = NotificationLog.objects.create(
            notification=self.notification,
            channel=NotificationChannel.EMAIL,
            status=NotificationStatus.SENT,
            attempt_count=1
        )
    
    def test_log_creation(self):
        """Test log creation"""
        self.assertEqual(self.log.notification, self.notification)
        self.assertEqual(self.log.channel, NotificationChannel.EMAIL)
        self.assertEqual(self.log.status, NotificationStatus.SENT)
        self.assertEqual(self.log.attempt_count, 1)
    
    def test_string_representation(self):
        """Test string representation of log"""
        expected = f"Test Notification - email - sent"
        self.assertEqual(str(self.log), expected)


class NotificationAPITest(APITestCase):
    """Test cases for Notification API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.EVENT_REMINDER,
            title='Test Notification',
            message='This is a test notification'
        )
    
    def test_list_notifications(self):
        """Test listing notifications"""
        response = self.client.get('/api/notifications/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_notification(self):
        """Test creating a notification"""
        data = {
            'notification_type': NotificationType.EVENT_UPDATE,
            'title': 'New Notification',
            'message': 'This is a new notification'
        }
        response = self.client.post('/api/notifications/notifications/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 2)
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        response = self.client.post(f'/api/notifications/notifications/{self.notification.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, NotificationStatus.READ)
    
    def test_mark_all_read(self):
        """Test marking all notifications as read"""
        # Create another notification
        Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.EVENT_UPDATE,
            title='Another Notification',
            message='Another test notification'
        )
        
        response = self.client.post('/api/notifications/notifications/mark_all_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check all notifications are marked as read
        unread_count = Notification.objects.filter(
            recipient=self.user,
            status__in=[NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.DELIVERED]
        ).count()
        self.assertEqual(unread_count, 0)
    
    def test_bulk_update_notifications(self):
        """Test bulk updating notifications"""
        # Create another notification
        notification2 = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.EVENT_UPDATE,
            title='Another Notification',
            message='Another test notification'
        )
        
        data = {
            'notification_ids': [self.notification.id, notification2.id],
            'action': 'mark_read'
        }
        
        response = self.client.post('/api/notifications/notifications/bulk_update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check both notifications are marked as read
        self.notification.refresh_from_db()
        notification2.refresh_from_db()
        self.assertEqual(self.notification.status, NotificationStatus.READ)
        self.assertEqual(notification2.status, NotificationStatus.READ)
    
    def test_get_notification_stats(self):
        """Test getting notification statistics"""
        response = self.client.get('/api/notifications/notifications/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_notifications'], 1)
        self.assertEqual(data['unread_count'], 1)
        self.assertEqual(data['pending_count'], 1)


class NotificationTemplateAPITest(APITestCase):
    """Test cases for NotificationTemplate API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.template = NotificationTemplate.objects.create(
            name='Test Template',
            notification_type=NotificationType.EVENT_REMINDER,
            title_template='Test: {title}',
            message_template='Test message: {message}'
        )
    
    def test_list_templates(self):
        """Test listing templates"""
        response = self.client.get('/api/notifications/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_templates_by_type(self):
        """Test getting templates by notification type"""
        response = self.client.get('/api/notifications/templates/by_type/?type=event_reminder')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class NotificationPreferenceAPITest(APITestCase):
    """Test cases for NotificationPreference API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            notification_type=NotificationType.EVENT_REMINDER,
            in_app_enabled=True,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True
        )
    
    def test_list_preferences(self):
        """Test listing preferences"""
        response = self.client.get('/api/notifications/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_preferences_summary(self):
        """Test getting preferences summary"""
        response = self.client.get('/api/notifications/preferences/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('event_reminder', data)
        self.assertTrue(data['event_reminder']['in_app'])
        self.assertTrue(data['event_reminder']['email'])
        self.assertFalse(data['event_reminder']['sms'])
        self.assertTrue(data['event_reminder']['push'])
    
    def test_bulk_update_preferences(self):
        """Test bulk updating preferences"""
        data = {
            'preferences': [
                {
                    'notification_type': NotificationType.EVENT_REMINDER,
                    'sms_enabled': True,
                    'push_enabled': False
                }
            ]
        }
        
        response = self.client.post('/api/notifications/preferences/bulk_update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check preference was updated
        self.preference.refresh_from_db()
        self.assertTrue(self.preference.sms_enabled)
        self.assertFalse(self.preference.push_enabled)


class NotificationChoiceAPITest(APITestCase):
    """Test cases for notification choice API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_get_notification_types(self):
        """Test getting notification types"""
        response = self.client.get('/api/notifications/types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_get_notification_priorities(self):
        """Test getting notification priorities"""
        response = self.client.get('/api/notifications/priorities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_get_notification_statuses(self):
        """Test getting notification statuses"""
        response = self.client.get('/api/notifications/statuses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_get_notification_channels(self):
        """Test getting notification channels"""
        response = self.client.get('/api/notifications/channels/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
