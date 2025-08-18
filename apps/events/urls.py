from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Main event endpoints
    path('', views.EventListView.as_view(), name='event-list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    
    # User-specific endpoints
    path('my-events/', views.UserEventsView.as_view(), name='user-events'),
    
    # Specialized event views
    path('nearby/', views.NearbyEventsView.as_view(), name='nearby-events'),
    path('open/', views.OpenEventsView.as_view(), name='open-events'),
    
    # Event status management
    path('<int:pk>/toggle-status/', views.toggle_event_status, name='toggle-event-status'),
    path('<int:pk>/toggle-active/', views.toggle_event_active, name='toggle-event-active'),
]
