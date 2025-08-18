from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'templates', views.NotificationTemplateViewSet, basename='notification-template')
router.register(r'preferences', views.NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'logs', views.NotificationLogViewSet, basename='notification-log')
router.register(r'types', views.NotificationTypeViewSet, basename='notification-type')
router.register(r'priorities', views.NotificationPriorityViewSet, basename='notification-priority')
router.register(r'statuses', views.NotificationStatusViewSet, basename='notification-status')
router.register(r'channels', views.NotificationChannelViewSet, basename='notification-channel')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
