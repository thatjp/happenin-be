from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    
    # Password management
    path('password/change/', views.ChangePasswordView.as_view(), name='password_change'),
    
    # Admin only
    path('users/', views.user_list, name='user_list'),
]
