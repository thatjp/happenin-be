from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationType, NotificationPriority, NotificationStatus,
    NotificationChannel, NotificationLog
)
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationUpdateSerializer,
    NotificationBulkUpdateSerializer, NotificationTemplateSerializer,
    NotificationTemplateCreateSerializer, NotificationTemplateUpdateSerializer,
    NotificationPreferenceSerializer, NotificationPreferenceUpdateSerializer,
    NotificationLogSerializer, NotificationStatsSerializer,
    NotificationTypeSerializer, NotificationPrioritySerializer,
    NotificationStatusSerializer, NotificationChannelSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'status', 'priority', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return notifications for the current user"""
        return Notification.objects.filter(recipient=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        """Set the recipient to the current user"""
        serializer.save(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications count"""
        unread_count = self.get_queryset().filter(
            status__in=[NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.DELIVERED]
        ).count()
        
        return Response({
            'unread_count': unread_count
        })

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})

    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """Mark a notification as unread"""
        notification = self.get_object()
        notification.status = NotificationStatus.DELIVERED
        notification.read_at = None
        notification.save()
        return Response({'status': 'marked as unread'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().filter(
            status__in=[NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.DELIVERED]
        ).update(
            status=NotificationStatus.READ,
            read_at=timezone.now()
        )
        return Response({'status': 'all notifications marked as read'})

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update notifications"""
        serializer = NotificationBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        action = serializer.validated_data['action']
        
        notifications = self.get_queryset().filter(id__in=notification_ids)
        
        if action == 'mark_read':
            notifications.update(
                status=NotificationStatus.READ,
                read_at=timezone.now()
            )
            message = f'{notifications.count()} notifications marked as read'
        elif action == 'mark_unread':
            notifications.update(
                status=NotificationStatus.DELIVERED,
                read_at=None
            )
            message = f'{notifications.count()} notifications marked as unread'
        elif action == 'delete':
            count = notifications.count()
            notifications.delete()
            message = f'{count} notifications deleted'
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'status': message})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics for the current user"""
        queryset = self.get_queryset()
        
        stats = {
            'total_notifications': queryset.count(),
            'unread_count': queryset.filter(
                status__in=[NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.DELIVERED]
            ).count(),
            'pending_count': queryset.filter(status=NotificationStatus.PENDING).count(),
            'sent_count': queryset.filter(status=NotificationStatus.SENT).count(),
            'failed_count': queryset.filter(status=NotificationStatus.FAILED).count(),
            'by_type': dict(queryset.values_list('notification_type').annotate(count=Count('id'))),
            'by_priority': dict(queryset.values_list('priority').annotate(count=Count('id')))
        }
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification templates"""
    queryset = NotificationTemplate.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['notification_type', 'is_active']
    search_fields = ['name', 'title_template', 'message_template']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return NotificationTemplateCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NotificationTemplateUpdateSerializer
        return NotificationTemplateSerializer

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get templates by notification type"""
        notification_type = request.query_params.get('type')
        if notification_type:
            templates = self.get_queryset().filter(
                notification_type=notification_type,
                is_active=True
            )
        else:
            templates = self.get_queryset().filter(is_active=True)
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification preferences"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type']

    def get_queryset(self):
        """Return preferences for the current user"""
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action in ['update', 'partial_update']:
            return NotificationPreferenceUpdateSerializer
        return NotificationPreferenceSerializer

    def perform_create(self, serializer):
        """Set the user to the current user"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of notification preferences"""
        preferences = self.get_queryset()
        
        summary = {}
        for pref in preferences:
            summary[pref.notification_type] = {
                'in_app': pref.in_app_enabled,
                'email': pref.email_enabled,
                'sms': pref.sms_enabled,
                'push': pref.push_enabled
            }
        
        return Response(summary)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update notification preferences"""
        preferences_data = request.data.get('preferences', [])
        
        updated_count = 0
        for pref_data in preferences_data:
            notification_type = pref_data.get('notification_type')
            if notification_type:
                preference, created = NotificationPreference.objects.get_or_create(
                    user=request.user,
                    notification_type=notification_type,
                    defaults={
                        'in_app_enabled': pref_data.get('in_app_enabled', True),
                        'email_enabled': pref_data.get('email_enabled', True),
                        'sms_enabled': pref_data.get('sms_enabled', False),
                        'push_enabled': pref_data.get('push_enabled', True)
                    }
                )
                
                if not created:
                    for field in ['in_app_enabled', 'email_enabled', 'sms_enabled', 'push_enabled']:
                        if field in pref_data:
                            setattr(preference, field, pref_data[field])
                    preference.save()
                    updated_count += 1
                else:
                    updated_count += 1
        
        return Response({
            'status': f'{updated_count} preferences updated',
            'updated_count': updated_count
        })


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing notification logs"""
    queryset = NotificationLog.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['channel', 'status']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        """Return logs for notifications belonging to the current user"""
        return NotificationLog.objects.filter(
            notification__recipient=self.request.user
        )


class NotificationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification types"""
    queryset = NotificationType.choices
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Return list of notification types"""
        types = [
            {'value': choice[0], 'display_name': choice[1]}
            for choice in self.queryset
        ]
        serializer = self.get_serializer(types, many=True)
        return Response(serializer.data)


class NotificationPriorityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification priorities"""
    queryset = NotificationPriority.choices
    serializer_class = NotificationPrioritySerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Return list of notification priorities"""
        priorities = [
            {'value': choice[0], 'display_name': choice[1]}
            for choice in self.queryset
        ]
        serializer = self.get_serializer(priorities, many=True)
        return Response(serializer.data)


class NotificationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification statuses"""
    queryset = NotificationStatus.choices
    serializer_class = NotificationStatusSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Return list of notification statuses"""
        statuses = [
            {'value': choice[0], 'display_name': choice[1]}
            for choice in self.queryset
        ]
        serializer = self.get_serializer(statuses, many=True)
        return Response(serializer.data)


class NotificationChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification channels"""
    queryset = NotificationChannel.choices
    serializer_class = NotificationChannelSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """Return list of notification channels"""
        channels = [
            {'value': choice[0], 'display_name': choice[1]}
            for choice in self.queryset
        ]
        serializer = self.get_serializer(channels, many=True)
        return Response(serializer.data)
