"""
URL configuration for happenin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home, name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import path, include
import os

def health(request):
    return HttpResponse("OK")

def debug_env(request):
    return JsonResponse({
        'DB_HOST': os.getenv('DB_HOST', 'NOT_SET'),
        'DB_NAME': os.getenv('DB_NAME', 'NOT_SET'),
        'DB_USER': os.getenv('DB_USER', 'NOT_SET'),
        'DB_PASSWORD': '***' if os.getenv('DB_PASSWORD') else 'NOT_SET',
        'SECRET_KEY': '***' if os.getenv('SECRET_KEY') else 'NOT_SET',
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health),
    path('debug/env/', debug_env),

    # API v1 endpoints (primary)
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/events/', include('apps.events.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
]
